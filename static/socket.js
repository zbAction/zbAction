(function(window, undefined){
	var Socket = function(){
		if(!(this instanceof Socket))
			return new Socket();

		this._events = {};
	};

	Socket.prototype._ws = null;
	Socket.prototype._onload = null;
	Socket.prototype._onclose = null;

	Socket.prototype.on = function(evt, fn){
		if(!evt) throw 'No event specified.';
		if(!fn) throw 'No callback specified.';

		this._events[evt] = this._events[evt] || [];
		this._events[evt].push(fn);
	};

	Socket.prototype.off = function(evt, fn){
		if(!evt || evt in this._events === false)
			return;

		if(fn === undefined){
			delete this._events[evt];
			return;
		}

		var index = this._events[evt].indexOf(fn);
		this._events[evt].splice(index, 1);
	};

	Socket.prototype.emit = function(evt){
		if(!evt || evt in this._events === false)
			return;

		for(var n = 0; n < this._events[evt].length; n++){
			var func = this._events[evt][n];
			var real_args = Array.prototype.slice.call(arguments, 1);

			func.apply(this, real_args);
		}
	};

	Socket.prototype.load = function(url){
		this._ws = new WebSocket(url);
		var that = this;

		this._ws.onopen = function(){
			if(that._onload)
				that._onload.apply(that, arguments);
		};

		this._ws.onmessage = function(e){
			var data = JSON.parse(e.data);
			that.emit(data.event, data);
		};

		this._ws.onclose = function(){
			if(that._onclose)
				that._onclose.apply(that, arguments);
				
			// Dispose of old connection.
			that._ws = null;
		}
	};

	Socket.prototype.onload = function(fn){
		this._onload = fn;
	};

	Socket.prototype.send = function(data){
		if(!this._ws)
			throw 'You must connect to a websocket first.';

		this._ws.send(JSON.stringify(data));
	};

	Socket.prototype.onclose = function(fn){
		this._onclose = fn;
	};

	window.Socket = Socket;
})(window);

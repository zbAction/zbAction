(function(window, undefined){
	var Socket = function(){
		if(!(this instanceof Socket))
			return new Socket();

		this._events = {};
	};

	Socket.prototype._ws = null;
	Socket.prototype._onload = null;

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

			(function(data){
				setTimeout(function(){
					that.emit(data.event, data);
				}, 0);
			})(data)
		};
	};

	Socket.prototype.onload = function(fn){
		this._onload = fn;
	};

	Socket.prototype.send = function(data){
		if(!this._ws)
			throw 'You must connect to a websocket first.';

		this._ws.send(JSON.stringify(data));
	};

	window.Socket = Socket;
})(window);
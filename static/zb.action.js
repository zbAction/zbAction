// Assumes socket.js is loaded
// $.zb.stat.mid = current logged in UID

(function(window, Socket, undefined){
	var SOCKET_URL;
	var MOD_URL;

	if(location.href.indexOf('localhost:') !== -1){
		SOCKET_URL = 'ws://localhost:4242/sync';
		MOD_URL = 'http://localhost:4343/mods/list/';
	}
	else{
		SOCKET_URL = 'ws://zbaction.reticent.io/sync';
		MOD_URL = 'http://zbaction.reticent.io/mods/list/';
	}
 
	var ACTION_TEMPLATE = {
		event: 'string',
		details: 'OBJECT',
		source: {
			uid: 0,
			board: 'string'
		},
		receiver: {
			uid: 0,
			board: 'string'
		}
	};

	var CURRENT_USER = {
		board_key: __zbAction.board_key,
		uid: $.zb.stat.mid,
		name: 'andrew' // $('#top_info a[href*="/profile/"]').text()
	};

	var zbAction = function(){
		if(!(this instanceof zbAction))
			return new zbAction();

		var ws = Socket();
		var that = this;

		this._wait = [];

		ws.onload(function(){
			ws.send({
				key: 0,
				type: 'handshake',
				data: CURRENT_USER
			});
		});

		ws.load(SOCKET_URL);

		// zbAction objects do not have create methods
		// until after their initial handshake. This is
		// so that API keys are always sent with actions.
		//
		// User keys are received from handshakes.
		//
		// Action details can be anything (pretty much anything)
		// as they are translated into a JSON string.

		// Registered is called as a bind to its corresponding
		// ModWrapper object.
		var register = function(key, evt, fn){
			// Reserved means reserved.
			if(_reserved_keys.hasOwnProperty(evt))
				return;

			var that = this;

			ws.on(key + '.' + evt, function(resp){
				resp.event = resp.event.replace(key + '.', '');
				fn.call(that, resp);
			});
		};

		var ModWrapper = function(send, key){
			this.send = send.bind(null, key);
			this.register = register.bind(this, key);
		};

		var load_approved = function(data){
			var approved = data.mods || [];

			for(var n = 0; n < that._wait.length; n++){
				var fn = that._wait[n];

				if(approved.indexOf(fn.key) !== -1)
					fn.fn.call(null, new ModWrapper(send, fn.key));
			}
			
			ws.send({
				key: 0,
				type: 'get_unread',
				data: CURRENT_USER
			});
		};

		// This is defined on handshake receive.
		// This is because we need to create a wrapper
		// that will accept a mod key and user key
		// in addition to whatever data needs to be sent.
		//
		// Note that this is not bound to anything
		// as it is used as send.bind(null, ...)
		var send = null;

		var _reserved_keys = {
			'handshake': function(data){
				// This caused me a lot of grief with
				// duplicate everything and tabs seemingly
				// being able to send stuff through others.
				if(send !== null) return;

				var USER_KEY = data.details;

				send = function(mod_key, data){
					try{
						if(!data.receiver.board_key)
							data.receiver.board_key = CURRENT_USER.board_key;

						if(data.receiver.board_key !== CURRENT_USER.board_key)
							throw new Error('Cross-board requests are not allowed.');

						// The real send data is constructed here.
						// The action data given by developers is
						// only additional data to fill in the blanks.
						if(data.details instanceof Object)
							data.details = JSON.stringify(data.details);

						data = {
							event: mod_key + '.' + data.event,
							details: data.details,
							source: CURRENT_USER,
							receiver: {
								uid: parseInt(data.receiver.uid),
								// Cross-board is currently disabled but this is here
								// in the event I decide to enable it for certain boards.
								board_key: data.receiver.board_key
							}
						};
					}
					catch(e){
						if(e.name === 'TypeError')
							throw new Error('Invalid action data provided.');

						throw e;
					}

					ws.send({
						key: USER_KEY,
						mod_key: mod_key,
						type: 'action',
						data: data
					});
				};

				$.getJSON(MOD_URL + __zbAction.board_key, load_approved);
			}
		};

		for(var key in _reserved_keys)
			if(_reserved_keys.hasOwnProperty(key))
				ws.on(key, _reserved_keys[key]);
	};

	zbAction.prototype.ready = function(key, fn){
		if(typeof key !== 'string')
			throw 'You must specify an API key.';
		if(typeof fn !== 'function')
			throw 'You must specify a function.';

		this._wait.push({key: key, fn: fn});
	};

	window.zbAction = new zbAction();
})(window, Socket);
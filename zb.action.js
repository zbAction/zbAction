// Assumes socket.js is loaded
// $.zb.stat.mid = current logged in UID

(function(window, Socket, undefined){
	var SOCKET_URL = 'ws://localhost:4242/sync';
 
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
		name: 'andrew' // $('#top_info strong a').text()
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

		var register = function(evt, fn){
			// Reserved means reserved.
			if(_reserved_keys.hasOwnProperty(evt))
				return;

			ws.on(evt, fn);
		};

		var ModWrapper = function(send, key){
			this.send = send.bind(null, key);
			this.register = register;
		};

		var _reserved_keys = {
			'handshake': function(data){
				var USER_KEY = data.details;

				var send = function(mod_key, data){
					try{
						if(CURRENT_USER.board_key !== data.receiver.board_key)
							throw new Error('Cross-board requests are not allowed.');

						// The real send data is constructed here.
						// The action data given by developers is
						// only additional data to fill in the blanks.
						data = {
							event: data.event + '',
							details: JSON.stringify(data.details),
							source: CURRENT_USER,
							receiver: {
								uid: parseInt(data.receiver.uid),
								board_key: data.receiver.board_key + ''
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

				that._wait.forEach(function(fn){
					fn.fn.call(null, new ModWrapper(send, fn.key));
				});
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
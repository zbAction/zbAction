// Assumes socket.js is loaded
// $.zb.stat.mid = current logged in UID

(function(window, Socket, undefined){
    var SOCKET_URL;
    var MOD_URL;
    var USER_URL;

    if(location.href.indexOf('localhost:') !== -1){
        SOCKET_URL = 'ws://localhost:4242/gateway';
        MOD_URL = 'http://localhost:4343/api/mods/list/';
        USER_URL = 'http://localhost:4343/api/users/list/';
    }
    else{
        SOCKET_URL = 'wss://zbaction.reticent.io/gateway';
        MOD_URL = 'https://zbaction.reticent.io/api/mods/list/';
        USER_URL = 'https://zbaction.reticent.io/api/users/list/';
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

    var HEARTBEAT_TIMEOUT = 10000 // 10 seconds.
    var RECONNECT_DELAY = 5000 // 5 seconds.

    var USER_LIST = {};

    var USER = {
        by_uid: function(uid){
            uid = '' + uid;

            return USER_LIST[uid] || null;
        },

        by_name: function(name){
            for(var test in USER_LIST)
                if(USER_LIST[test] === name)
                    return test;

            return null;
        }
    };

    var BOARD_KEY = window.__zbAction.board_key;

    // Disallow automated board key viewing. If
    // somebody wants to view a board key they'll have
    // to view the source. This prevents malicious users
    // from stealing keys using scripts. Or at least it
    // tries to. At the very least this will make zbAction
    // mods unable to steal board keys.
    delete window.__zbAction;

    var zbAction = function(){
        if(!(this instanceof zbAction))
            return new zbAction();

        var ws = Socket();
        var that = this;

        this._wait = {};
        var _error = [];

        var CURRENT_USER = {
            board_key: BOARD_KEY,
            bpath: $.zb.stat.bpath,
            uid: $.zb.stat.mid,
            name: $('#top_info strong a[href*="/profile/"]').text()
        };

        ws.onload(function(){
            ws.send({
                key: 0,
                type: 'handshake',
                data: CURRENT_USER
            });
        });

        var ready_load = function(){
            $(document).ready(function(){
                // This is set one more time in the event
                // the DOM is not loaded. So basically if people
                // put this script somewhere that isn't in the below
                // the board section.
                CURRENT_USER.name = $('#top_info strong a[href*="/profile/"]').text();

                ws.load(SOCKET_URL);
            });
        };

        ready_load();

        ws.onclose(function(){
            _error.forEach(function(fn){
                fn.call(that);
            });
        });

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

        var error = function(fn){
            _error.push(fn);
        };

        var ModWrapper = function(send, key){
            this.send = send.bind(null, key);
            this.register = register.bind(this, key);
            this.users = USER;
            this.error = error;
        };

        var get_unread = function(){
            ws.send({
                key: 0,
                type: 'get_unread',
                data: CURRENT_USER
            });
        };

        var load_approved = function(data){
            var approved = data.mods || [];

            for(var key in that._wait)
                if(approved.indexOf(key) !== -1)
                    that._wait[key].call(null, new ModWrapper(send, key));

            get_unread();
        };

        var heartbeat = function(){
            var latest = new Date();

            ws.on('heartbeat', function(){
                latest = new Date();
            });

            ws.send({
                key: 0,
                type: 'heartbeat',
                data: 'heartbeat'
            });

            var check = function(){
                var now = new Date();

                // Slack for latency.
                if(now - latest > HEARTBEAT_TIMEOUT + 1){
                    try{
                        // Reset.
                        ws.load(SOCKET_URL);
                        get_unread();
                        heartbeat();
                    }
                    catch(e){
                        // Fail silently.
                    }
                }
                else{
                    setTimeout(check, HEARTBEAT_TIMEOUT);
                }
            };

            setTimeout(check, HEARTBEAT_TIMEOUT);
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
                        data.details = JSON.stringify(data.details);

                        data = {
                            event: (mod_key + '.' + data.event).substring(0, 255),
                            details: data.details.substring(0, 10000),
                            source: CURRENT_USER,
                            timestamp: data.timestamp,
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

                    try{
                        ws.send({
                            key: USER_KEY,
                            mod_key: mod_key,
                            type: 'action',
                            data: data
                        });
                    }
                    catch(e){
                        throw new Error('Not connected to zbAction server.');
                    }
                };

                $.getJSON(USER_URL + CURRENT_USER.board_key, function(resp){
                    USER_LIST = resp.users;
                }).done(function(){
                    heartbeat();
                    $.getJSON(MOD_URL + CURRENT_USER.board_key).then(load_approved);
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

        this._wait[key] = fn;
    };

    window.zbAction = new zbAction();
})(window, Socket);

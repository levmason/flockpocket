function API (fp) {
    var self = this;

    self.handlers = {};
    self.sock_url = utility.ws_url('api');
    self.disconnect_timeout = 20000;

    /*
     * Functions for handling the websockets connection
     */

    /* initialize the api connection */
    self.open = function () {
        // connect the socket
        self.sock = new WebSocket(self.sock_url);

        // set websocket handlers
        self.sock.onmessage = self.sock_rx;
        self.sock.onclose = self.sock_onclose;
        self.sock.onopen = self.sock_onopen;
    }

    /* close the api connection */
    self.close = function () {
        self.sock.onclose = null;
        self.sock.close()
    }

    /* what to do when the websocket opens */
    self.sock_onopen = function (e) {
        fp.set_connected();
        self.query('ui_config');
        //self.keepalive();
    }

    /* what to do when the websocket closes */
    self.sock_onclose = function (e) {
        fp.set_disconnected();
        // Try to reconnect in 1 seconds
        setTimeout(function(){
            try {
                self.open();
            } catch (err) {}
        }, 1000);
    }

    /* detect when the connection has gone down */
    self.keepalive = function () {
        // reset the disconnect timeout
        try {
            clearTimeout(self.disconnect_timeout);
        } catch {}
        // set a new timeout
        self.disconnect_timeout = setTimeout(function () {
            self.sock.close();
        }, self.disconnect_timeout);
    }

    /* send an api query */
    self.query = function (query) {
        if (self.sock.readyState === WebSocket.OPEN) {
            self.sock.send(JSON.stringify(query));
        }
    }

    /* handle api response */
    self.sock_rx = function (e) {
        let data = JSON.parse(e.data);
        if (data.error) {
            modal.alert(data.error);
            return;
        }

        let handler = self[data.name];
        let view_handler = self.handlers[data.name];
        if (!(handler || view_handler)) {
            modal.alert(`No api handler for ${data.name}`);
        } else {
            // run the default handler
            if (handler) {
                handler(data.options);
            }
            // run the view-specific handler
            if (view_handler) {
                view_handler(data.options);
            }
        }
    }

    /* default handlers */
    self.ui_config = function (data) {
	console.log(data);
        fp.user_d = data.user_d || {};
        fp.thread_d = data.thread_d || {};

        // set the picture urls
        for (let id in fp.user_d) {
            let user = fp.user_d[id];
            user.pic_url = utility.static_url('profile_pics/'+ (user.pic || "avatar.svg"));
        }
        fp.user = fp.user_d[data.user_id];

        fp.init_ui();
        window.onhashchange();
        utility.unblockUI();
    }

    /* chat */
    self.message = function (options) {
        let message = options.message;
        if (message.user != fp.user.id) {
            let icon = fp.user_d[message.user].pic_url;
            utility.notify("New Message!", message.text, icon, 'chat');
        }
    }

    /* new thread */
    self.new_thread = function (options) {
        fp.thread_d[options.id] = options;
    }

    /* user update */
    self.user = function (user) {
	// set the img link
	user.pic_url = utility.static_url('profile_pics/'+ (user.pic || "avatar.svg"));

	// store in dictionary
	fp.user_d[user.id] = user;
	if (user.id == fp.user.id) {
	    fp.user = user;
	}
    }

    self.open();
}

function API (fp) {
    var self = this;

    self.handler_elements = {};
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

        for (let name in data) {
            let opt = data[name];
            let handler;

            for (let label in self.handler_elements) {
                let el_handler = self.handler_elements[label];
                handler = el_handler[name];
                if (handler) {
                    handler(opt);
                }
            }
        }
    }

    self.register = function (obj, label) {
        if (obj.handler) {
            label = label || obj.constructor.name;
            self.handler_elements[label] = obj.handler;
        }
    }

    self.unregister = function (obj, label) {
        label = label || obj.constructor.name;
        delete self.handler_elements[label];
    }

    self.open();
}

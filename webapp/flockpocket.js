function flockpocket () {
    var self = this;
    self.connected = true;
    self.user_d = null;
    self.user = null;
    self.thread_d = {};
    self.user_thread_d = {};
    self.auth = !location.href.includes("user_activate");
    self.hash = window.location.hash.substring(1);
    self.active = false;
    self.activeTimeout = null;
    self.content = null;

    self.init = function () {
        if (self.auth) {
            utility.blockUI();

            // Add elements
            self.api = new API(self);

            // register with the api
            self.api.register(self);
        } else {
            let id = location.href.split("/")[4];
            new top_menu($("#top_menu"), false);
            new new_user($("#content"), id);
        }
    }

    self.init_handlers = function () {
        $(document).on("click input", function(e) {
            self.set_active();
        })

        scroll_autohide(self, $('#content'));
    }

    self.set_active = function () {
        if (!self.active) {
            if (self.content && self.content.on_active) {
                self.content.on_active();
            }
            fp.api.query({
                'send_active': {
                    active: true,
                }
            })
        }
        self.active = true;
        if (self.active_timeout) {
            clearTimeout(self.active_timeout);
        }
        self.active_timeout = setTimeout(() => {
            self.unset_active();
            self.active_timeout = null;
        }, 60000);
    }

    self.unset_active = function () {
        self.active = false;
        fp.api.query({
            'send_active': {
                active: false,
            }
        })
    }

    self.init_ui = function () {
        self.menu = new menu($("#leftbar"));
        self.top_menu = new top_menu($("#top_menu"));
        self.chat = new chat($("#rightbar"));

        self.init_handlers();
    }

    self.filter_users = function(search, include_me, gender) {
        let filtered_user_d = {};
        search = '^' + search;

        for (let id in self.user_d) {
            let user = self.user_d[id];
            let regex = new RegExp(search, "i");
            let labels = user.full_name.split(/[\s\/]+/);
            if ((include_me || id != fp.user.id) &&
                (!gender || user.gender == gender)) {
                for (var lbl of labels) {
                    if (lbl.search(regex) >= 0) {
                        filtered_user_d[id] = user;
                    }
                }
            }
        }

        return filtered_user_d;
    }

    self.filter_threads = function(search) {
        let filtered_thread_d = {};
        search = '^' + search;

        for (let id in self.thread_d) {
            let thread = self.thread_d[id];
            let regex = new RegExp(search, "i");
            let labels = (thread.label || thread.user.full_name).split(/[\s\/]+/);
            for (var lbl of labels) {
                if (lbl.search(regex) >= 0) {
                    filtered_thread_d[id] = thread;
                    break;
                }
            }
        }

        return filtered_thread_d;
    }

    self.set_connected = function () {
        if (!self.connected) {
            $.unblockUI();
        }
        self.connected = false;
    }

    self.set_disconnected = function () {
        utility.blockUI("Disconnected :-(");
        self.connected = false;
    }

    self.set_hash = function(path) {
        document.location.hash = path;
    }

    window.onhashchange = function(e) {
        // clear the api handlers
        if (self.content) {
            self.api.unregister(self.content);
        }

	// get the page hash
        self.hash = window.location.hash.substring(1);
        let [page, id] = self.hash.split("/");

	// remove selected menu item
        $('div.menu_item').removeClass("selected");
	if (page) {
	    $(`div.menu_item#${page}`).addClass("selected");
	}

        switch(page) {
        case "directory":
	    if (id) {
		self.content = new profile($('#content'), self.user_d[id]);
	    } else {
		self.content = new directory($("#content"));
	    }
            break
        case "settings":
            self.content = new settings($("#content"));
            break
        case "setup":
            self.content = new initial_setup($("#content"));
            break
        case "invite_user":
            self.content = new invite_user($("#content"));
            break
        case "chat":
            if (id) {
                self.content = new chat_thread($("#content"), id);
            } else {
                //self.chat = new chat($("#content"));
            }
            break;
        case "logout":
            window.location.href = "/logout";
            break;
        }

        self.set_active();
    }

    /*
     * websocket handlers
     */
    self.handler = {
        /* The initial configuration is received */
        ui_config:  function (opt) {
            console.log(opt)
            self.user_d = opt.user_d || {};

            // initialize the user objects
            for (let id in self.user_d) {
                let user_cfg = self.user_d[id];
                self.user_d[id] = new user_object(user_cfg);
            }
            self.user = self.user_d[opt.user_id];

            // initialize the threads
            for (let id in opt.thread_d) {
                let thread_cfg = opt.thread_d[id];
                let thread = new thread_object (thread_cfg);
                self.thread_d[id] = thread;
                if (thread.user) {
                    self.user_thread_d[thread.user.id] = thread
                }
            }

            /* this is required for django CSRF handling */
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                        // Only send the token to relative URLs i.e. locally.
                        xhr.setRequestHeader("X-CSRFToken", opt.csrf_token);
                    }
                }
            });

            self.init_ui();
            window.onhashchange();
            utility.unblockUI();
        },

        /* somebody sent a message */
        message: function (opt) {
            let message = opt.message;
            if (message.user != self.user.id) {
                let icon = self.user_d[message.user].pic_url;
                utility.notify("New Message!", message.text, icon, 'chat');
            }
        },

        /* A thread was created */
        new_thread: function (thread) {
            self.add_thread(thread);
        },

        /* a user was updated */
        user: function (user) {
	    // set the img link
	    user.pic_url = utility.static_url('profile_pics/'+ (user.pic || "avatar.svg"));

	    // store in dictionary
	    self.user_d[user.id] = user;
	    if (user.id == self.user.id) {
	        self.user = user;
	    }
        }
    }
}

$(document).ready(function(){
    os = navigator.platform;
    if (!(os.startsWith("Mac"))) {
        $('body').addClass('windows');
    }

    fp = new flockpocket();
    fp.init();
});




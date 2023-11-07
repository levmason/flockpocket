function flockpocket () {
    var self = this;
    self.connected = true;
    self.user_d = null;
    self.user = null;
    self.auth = !location.href.includes("user_activate");
    self.hash = window.location.hash.substring(1);

    self.init = function () {
        if (self.auth) {
            utility.blockUI();

            // Add elements
            self.api = new API(self);
        } else {
            let id = location.href.split("/")[4];
            new top_menu($("#top_menu"), false);
            new new_user($("#content"), id);
        }
    }

    self.init_ui = function () {
        self.menu = new menu($("#left_menu"));
        self.top_menu = new top_menu($("#top_menu"));
        self.chat = new chat($("#rightbar"));
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
        self.api.handlers = {};

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
		new profile($('#content'), self.user_d[id]);
	    } else {
		new directory($("#content"));
	    }
            break
        case "settings":
            new settings($("#content"));
            break
        case "setup":
            new setup($("#content"));
            break
        case "invite_user":
            new invite_user($("#content"));
            break
        case "chat":
            if (id) {
                new chat_thread($("#content"), id);
            }
            break;
        case "logout":
            window.location.href = "/logout";
            break;
        }
    }


}

$(document).ready(function(){
    /* this is required for django CSRF handling */
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken",
                                     $("input[name=csrfmiddlewaretoken]").val());
            }
        }
    });

    fp = new flockpocket();
    fp.init();
});




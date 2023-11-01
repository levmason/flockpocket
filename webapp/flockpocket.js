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
    }

    self.filter_users = function(search, include_me, gender) {
        let filtered_user_d = {};

        for (let id in self.user_d) {
            let user = self.user_d[id];
            if ((include_me || id != fp.user.id) &&
                (user.full_name.search(new RegExp(search, "i")) >= 0) &&
                (!gender || user.gender == gender)) {
                filtered_user_d[id] = user;
            }
        }

        return filtered_user_d;
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

    window.onhashchange = function(e) {
        self.hash = window.location.hash.substring(1);
        let [page, id] = self.hash.split("/");
        switch(page) {
        case "profile":
            new profile($('#content'), self.user_d[id]);
            break;
        case "directory":
            new directory($("#content"));
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
            } else {
                new chat($("#content"));
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
    new Notification('Hi, How are you?');

    new Notification('Notification title', {
        body: 'Hey there! You\'ve been notified!',
    });
});




function user_menu (container, append = false) {
    var self = this;
    el.call(self, container, append);

    self.menu_d = {
        "Edit Profile": "settings",
        "Invite User": "invite_user",
        Logout: "logout",
    }

    // initialize the element
    self.init = function () {
        self.html = `
          <div id="user_menu">
            <img src="${fp.user.pic_url}">
            <div id="user_menu_items">`;

        for (var key in self.menu_d) {
            let hashtag = self.menu_d[key];

            let selected = (hashtag == fp.hash) ? "selected":"";
            self.html += `<div id="${hashtag}" class="menu_item ${selected}">${key}</div>`;
        }
        self.html += `</div></div>`;

        self.add_to_page();
        self.init_handlers();
    }

    // initialize handlers
    self.init_handlers = function () {
        self.el.on("click", "img", function() {
            $('div#user_menu_items').show();

            $(document).on("click", function (e) {
                $('div#user_menu_items').hide();
                $(document).off("click");
            })
            return false;
        });

        self.el.on("click", "div.menu_item", function (e) {
            $('div.menu_item').removeClass("selected");
            $(this).addClass("selected");

            let id = $(this).attr("id")
            document.location.hash = id;
        })

    }
}

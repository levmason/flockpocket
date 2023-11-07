function menu (container) {
    var self = this;
    el.call(self, container, false);

    self.menu_d = {
        Home: "home",
        Calendar: "calendar",
//        Chat: "chat",
        Directory: "directory",
        Community: "community",
    }

    // initialize
    self.init = function () {
        self.html += '<div id="menu">';

        for (var key in self.menu_d) {
            let hashtag = self.menu_d[key];

            let selected = (hashtag == fp.hash) ? "selected":"";
            self.html += `<div id="${hashtag}" class="menu_item ${selected}">${key}</div>`;
        }
        self.html += '</div>';

        self.add_to_page();
        self.init_handlers();
    }

    // initialize handlers
    self.init_handlers = function () {
        self.el.on("click", "div.menu_item", function (e) {
            let id = $(this).attr("id")
            document.location.hash = id;
        })
    }

    self.init();

}

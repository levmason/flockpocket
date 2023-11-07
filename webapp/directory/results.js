function results (container, search) {
    var self = this;
    el.call(self, container);

    self.search = search.toLowerCase();

    // initialize
    self.init = function () {
        self.html = '<div id="results"></div>';
        self.add_to_page();

        let filtered_user_d = fp.filter_users(self.search, true);

        for (let id in filtered_user_d) {
            let user = filtered_user_d[id];
            new badge (self.el, user, "search", append = true);
        }
    }

    self.init();
}

function chat_results (container, search) {
    var self = this;
    el.call(self, container);

    self.search = search.toLowerCase();

    // initialize
    self.init = function () {
        self.html = '<div id="results"></div>';
        self.add_to_page();

        let filtered_user_d = fp.filter_users(self.search, false);
        let filtered_thread_d = fp.filter_threads(self.search);
        for (let id in filtered_thread_d) {
            let thread = filtered_thread_d[id];
            if (thread.user) {
                filtered_thread_d[thread.user.id] = thread.user;
                delete filtered_thread_d[id];
            }
        }

        let thread_d = utility.merge(filtered_thread_d, filtered_user_d);
        for (let id in thread_d) {
            let user = thread_d[id];
            new chat_badge (self.el, null,  user);
        }
    }

    self.init();
}

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

        // remove users already having threads
        for (let id in filtered_thread_d) {
            let thread = filtered_thread_d[id];
            if (thread.user) {
                delete filtered_user_d[thread.user.id];
            }
        }

        // add existing threads
        for (let id in filtered_thread_d) {
            let thread = filtered_thread_d[id];
            new chat_badge (self.el, thread);
        }
        // add other users
        for (let id in filtered_user_d) {
            let user = filtered_user_d[id];
            new chat_badge (self.el, null,  user);
        }
    }

    self.init();
}

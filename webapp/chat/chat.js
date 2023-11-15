function chat (container, id) {
    var self = this;
    el.call(self, container);

    self.handler = {};

    // initialize the chat
    self.init = function () {
        self.html = `
          <div id="chat">
            <div class="header">Chat</div>
            <input type="search" placeholder="Search..."></input>
            <div id="results"></div>
          </div>`;

        self.add_to_page();

        self.search_el = self.el.find('input');
        self.results_el = self.el.find('div#results');

        self.set_to_recent();
        self.init_handlers();
    }

    self.init_handlers = function () {
        // register with the api
        fp.api.register(self);

        self.el.on("click", "div.thread_label", function () {
            let thread_id = $(this).attr("id");
            fp.set_hash("chat/" + thread_id);
        });

        self.search_el.on("input", function(e) {
            let filter = $(this).val();
            if (filter) {
                new chat_results (self.results_el, filter);
            } else {
                self.set_to_recent();
            }
        })

        self.el.on("click", "div.badge.thread", function () {
            let search = self.search_el.val();
            if (search) {
                self.search_el.val("");
                self.set_to_recent();
            }
        });
    }

    self.set_to_recent = function () {
        self.results_el.empty();

        let sorted_threads = Object.keys(fp.thread_d).sort(function(a, b) {
            return fp.thread_d[b].timestamp - fp.thread_d[a].timestamp;
        });

        for (var thread_id of sorted_threads) {
            let thread = fp.thread_d[thread_id];
            self.add_thread(thread);
        }
    }

    self.add_thread = function (thread) {
        new chat_badge(self.results_el, thread);
    }

    /*
     * api handlers
     */
    self.handler.new_thread = function (thread) {
        self.add_thread(thread);
    }

    self.handler.like = function (opt) {
        let thread = fp.thread_d[opt.thread];
        thread.timestamp = opt.timestamp;
        self.set_to_recent();
    }

    self.handler.message = function (opt) {
        let thread = fp.thread_d[opt.thread];
        thread.timestamp = opt.message.timestamp;
        self.set_to_recent();
    }

    self.init();
}

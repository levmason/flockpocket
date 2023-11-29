function chat (container, id) {
    var self = this;
    el.call(self, container);

    self.badge_d = {};
    self.first = null;
    self.handler = {};

    // initialize the chat
    self.init = function () {
        self.html = `
          <div id="chat">
            <div class="header">Chat</div>
            <div id="create_thread_btn">
              ${svg.plus}
            </div>
            <input type="search" placeholder="Search..."></input>
            <div id="results"></div>
          </div>`;

        self.add_to_page();

        self.creat_btn = self.el.find('div#create_thread_btn');
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
        self.first = null;
        self.results_el.empty();

        let sorted_threads = Object.keys(fp.thread_d).sort(function(a, b) {
            return fp.thread_d[b].timestamp - fp.thread_d[a].timestamp;
        });

        for (var thread_id of sorted_threads) {
            let thread = fp.thread_d[thread_id];
            self.add_thread(thread);
        }
    }

    self.set_most_recent = function (thread) {
        let badge = self.badge_d[thread.id];
        if (self.first != badge) {
            badge.el.insertBefore(self.first.el);
            self.first = badge;
        }
    }

    self.add_thread = function (thread) {
        let badge = new chat_badge(self.results_el, thread);
        self.badge_d[thread.id] = badge;
        if (!self.first) {
            self.first = badge;
        }
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
        self.set_most_recent(thread);
    }

    self.handler.message = function (opt) {
        let thread = fp.thread_d[opt.thread];
        thread.length++;
        thread.timestamp = opt.message.timestamp;
        // move to the top
        self.set_most_recent(thread);
        if (!thread.in_view()) {
            let badge = self.badge_d[thread.id];
            badge.el.addClass('unread');
        }
    }

    self.handler.active = function (opt) {
        let user = fp.user_d[opt.user_id];
        user.active = opt.active;
        $(`div#${user.id}.badge.thread`).toggleClass('active', opt.active);
    }

    self.handler.seen = function (opt) {
        let uid = opt.user;
        let thread = fp.thread_d[opt.thread];
        thread.seen[uid] = opt.message_idx;
    }

    self.init();
}

function chat_badge (container, thread, user = null) {
    var self = this;
    el.call(self, container, true);

    console.log(user);
    console.log(thread);
    if (user || thread.user) {
        self.user = user || thread.user;
        self.user_id = self.user.id;
        self.label = self.user.full_name;
        self.pic_html = `<img class="pic" src="${self.user.pic_url}">`;
        self.thread_id = `user=${self.user.id}`;
    } else {
        self.thread_id = thread.id;
        self.user_id = "";
        self.pic_html = thread.pic_svg;
        self.label = thread.label;
    }

    // see if the thread has unread content
    self.unread = thread && !thread.in_view() && thread.seen[fp.user.id] < thread.length-1;

    self.init = function () {
        let unread_class = self.unread ? "unread":"";
        let active_class = (self.user && self.user.active) ? "active":"";

        self.html = `
            <div class="badge thread ${active_class} ${unread_class}" id="${self.user_id}">
              ${self.pic_html}
              <svg class="active" height="10" width="10">
                <circle cx="5" cy="5" r="5"/>
              </svg>
              <div class="details">
                <span class="name">${self.label}</span>
                <svg class="unread" height="8" width="8">
                  <circle cx="4" cy="4" r="4"/>
                </svg>
              </div>
            </div>`;

        self.add_to_page();
        self.init_handlers();
    }

    self.init_handlers = function () {
        self.el.on("click", function () {
            self.el.removeClass("unread");
            document.location.hash = "chat/" + self.thread_id;
        });
    }

    self.init()
}

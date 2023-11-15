function chat_badge (container, thread, user = null) {
    var self = this;
    el.call(self, container, true);

    if (user || thread.user) {
        self.user = user || thread.user;
        self.label = self.user.full_name;
        self.pic_url = self.user.pic_url;
        self.thread_id = `user=${self.user.id}`;
    } else {
        self.thread_id = thread.id;
    }

    self.init = function () {
        self.html = `
            <div class="badge thread ${self.user.active ? "active":""}">
              <img class="pic" src="${self.pic_url}">
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
            document.location.hash = "chat/" + self.thread_id;
        });
    }

    self.init()
}

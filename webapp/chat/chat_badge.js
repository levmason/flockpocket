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
            <div class="badge thread">
              <img class="pic" src="${self.pic_url}">
              <div class="details">
                <span class="name">${self.label}</span>
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

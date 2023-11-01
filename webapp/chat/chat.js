function chat (container, id) {
    var self = this;
    el.call(self, container);

    // initialize the chat
    self.init = function () {
        self.html = `
          <div id="chat">`;

        for (var thread_id in fp.thread_d) {
            let thread = fp.thread_d[thread_id];
            self.html += `<div class="thread_label" id="${thread_id}">${thread.label}</div>`;
        }
        self.html += `</div>`;

        self.add_to_page();
        self.init_handlers();
    }

    self.init_handlers = function () {
        self.el.on("click", "div.thread_label", function () {
            let thread_id = $(this).attr("id");
            document.location.hash = "chat/" + thread_id;
        });
    }

    self.init();
}

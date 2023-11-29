function notification_menu (container, append = false) {
    var self = this;
    el.call(self, container, append);

    self.bell_url = utility.static_url("img/bell.svg");

    // initialize
    self.init = function () {
        self.html = `
          <div id="notifications">
            <img src="${self.bell_url}">
          </div>`;

        self.add_to_page();
    }

    self.init();
}

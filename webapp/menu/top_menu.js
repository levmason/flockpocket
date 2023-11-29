function top_menu (container, authorized = true) {
    var self = this;
    el.call(self, container);

    self.logo_url = utility.static_url("img/logo.svg");
    self.user_menu = null;

    // initialize
    self.init = function () {
        self.html = `
          <div id="logo">
            <img src="${self.logo_url}">
          </div>
          <div id="notifications">
            <img src="${self.bell_url}">
          </div>`;

        self.add_to_page();
        if (authorized) {
            new notification_menu (container, true);
            self.user_menu = new user_menu (container, true);
            self.user_menu.init();
        }
    }

    self.init();
}

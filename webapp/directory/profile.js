function profile (container, user) {
    var self = this;
    self.container = container;
    self.el = null;
    self.user = user;
    self.html = "";

    // initialize the badge
    self.init = function () {
        self.html = '<div class="profile"></div>';

        self.container.html(self.html);
        self.el = self.container.children().first();

        // badge
        self.badge = new badge(self.el, user, "profile");

        // family
        if (user.family) {
            new familycard(self.el, user.family);
        }

        // skills
        if (user.skills) {
            let text = "";
            for (var skill of user.skills) {
                text += skill + '<br>';
            }
            new infocard(self.el, "Occupations / Skills / Passions", text)
        }

        // about
        if (user.about) {
            new infocard(self.el, "About", user.about);
        }
    }

    self.init();
}

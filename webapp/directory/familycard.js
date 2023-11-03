function familycard (container, family, append = true) {
    var self = this;
    self.container = container;
    self.el = null;
    self.html = "";

    // initialize the badge
    self.init = function () {
        self.html = '<div class="card family">'+
            '<div class="label">Family</div>'+
            '<div class="family"></div>';

        // add to dom
        if (append) {
            self.container.append(self.html);
        } else {
            self.container.html(self.html);
        }
        self.el = self.container.children().last();

        for (let rel of family) {
            let user;
            if (rel.user_id) {
                user = fp.user_d[rel.user_id];
            } else {
                user = {
                    full_name: rel.name,
                    pic_url: utility.static_url("profile_pics/avatar.svg")
                };
            }
            let type = rel.type.capitalize();
            if (user) {
                new badge (self.el, user, "small", true, type);
            }
        }
    }

    self.init();
}

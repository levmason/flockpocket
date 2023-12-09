function badge (container, user, type, append = false, label = null) {
    var self = this;
    el.call(self, container, append);

    self.link = Boolean(user.id && !["profile", "family", "select", "selected"].includes(type));
    self.link_class = Boolean(user.id && !["profile", "selected"].includes(type)) ? "" : "nolink";
    self.chat_icon = utility.static_url('img/chat.svg');

    // initialize the badge
    self.init = function () {
        self.html = `<div id=${user.id} class="badge ${type} ${self.link_class}" >`;
        switch (type) {
        case "small":
            self.html += `
                <img class="pic" src="${user.pic_url}"><br>
                <span class="name">${user.full_name}</span>`;
            if (label) {
                self.html += `<br><span class="label">${label}</span>`;
            }
            break;
        case "search":
            self.html += `
                <img class="pic" src="${user.pic_url}">
                <div class="details">
                  <span class="name">${user.full_name}</span><br>
                  <span class="type">${user.membership_status}</span><br>
                  <span class="email">${user.email}</span> | <span class="phone">${user.phone}</span><br>
                  <span class="address">${user.address}</span>
                </div>`;
            break;
        case "family":
            self.html += `
                <img class="pic" src="${user.pic_url}">
                <div class="details">
                  <span class="name">${user.full_name}</span> | <span class="email">${user.email}</span>
                </div>`;
            break;
        case "select":
            self.html += `
                <img class="pic" src="${user.pic_url}">
                <div class="details">
                  <span class="name">${user.full_name}</span> | <span class="email">${user.email}</span>
                </div>`;
            break;
        case "selected":
            self.html += `
                <img class="pic" src="${user.pic_url}"><br>
                <span class="name">${user.full_name}</span>
                <span class="remove">X</span>`;
            break;
        case "profile":
            self.html += `
                <img class="pic" src="${user.pic_url}">
                <div class="details">
                  <span class="name">${user.full_name}</span><br>
                  <span class="type">${user.membership_status}</span><br>
                  <span class="phone"><a href-"tel: ${user.phone}">${user.phone}</a></span><br>
                  <span class="email"><a href="mailto: ${user.email}">${user.email}</a></span><br>
                  <span class="address">${user.address}</span><br>`;
            if (user != fp.user) {
                self.html += `
                  <button class="chat_me" />Send Message<img src="${utility.static_url('img/chat.svg')}" />
                  </button>`;
            }
            self.html += `</div>`;
            break;
        }
        self.html += '</div>';

        self.add_to_page();
        self.init_handlers();
    }

    self.init_handlers = function () {
        self.el.off("click");

        if (self.link) {
            self.el.on("click", function (e) {
                document.location.hash = 'directory/' + user.id;
            })
        } else {
            self.el.on("click", "button.chat_me", function (e) {
                document.location.hash = 'chat/user=' + user.id;
            })
        }
    }

    self.init();
}

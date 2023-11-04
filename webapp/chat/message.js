function message (container, config) {
    var self = this;
    el.call(self, container, "prepend");

    self.user = fp.user_d[config.user];
    self.me = Boolean(self.user == fp.user) ? "me":"";
    self.text = utility.emoticon_replace(config.text);
    self.timestamp = utility.getTimeString(config.timestamp);
    self.heart_img = utility.static_url("img/heart_outline.svg");

    self.init = function () {
        self.html = `
          <div class="message_wrapper">`;
        if (self.me) {
            self.html += `<div class="me_bar"></div>`;
        }
        self.html += `
            <img class="threadpic" src="${self.user.pic_url}">
            <div class="name">${self.user.full_name}</div>
            <div class="message">
              ${self.text}
              <div class="timestamp">${self.timestamp}</div>
              <div class="heart">
                <img src="${self.heart_img}" />
              </div>
            </div>
          </div>`;

        self.add_to_page();
    }

    self.update = function (msg) {
        let timestamp = utility.getTimeString(msg.timestamp);
        let text = utility.emoticon_replace(msg.text);
        self.el.append(`<div class="message">`+
                       `${text}<div class="timestamp">${timestamp}</div>`+
                       `<div class="heart"><img src="${self.heart_img}" /></div>`+
                       `</div>`);
    }

    self.init();
}

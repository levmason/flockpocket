function message (container, thread, config, idx) {
    var self = this;
    el.call(self, container, "prepend");

    self.idx = idx;
    self.thread = thread;
    self.like_l = config.like_l || [];
    self.user = fp.user_d[config.user];
    self.thread_id = config.thread_id;
    self.me = Boolean(self.user == fp.user) ? "me":"";
    self.text = utility.emoticon_replace(config.text);
    self.timestamp = utility.getTimeString(config.timestamp);
    self.heart_img = utility.static_url("img/heart_outline.svg");
    self.heart_full_img = utility.static_url("img/heart.svg");

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
              <div class="heart ${self.me ? "noclick":""}">
                <img src="${self.heart_img}" />
              </div>
            </div>
          </div>`;

        self.add_to_page();

        self.heart_el = self.el.find('div.heart');
        self.img_el = self.el.find('div.heart img');

        self.update_like();
        self.init_handlers();
    }

    self.update = function (msg) {
        let timestamp = utility.getTimeString(msg.timestamp);
        let text = utility.emoticon_replace(msg.text);
        self.el.append(`<div class="message">`+
                       `${text}<div class="timestamp">${timestamp}</div>`+
                       `<div class="heart ${self.me ? "noclick":""}">`+
                       `<img src="${self.heart_img}" /></div>`+
                       `</div>`);
    }

    self.update_like = function () {
        if (self.like_l.isEmpty()) {
            self.hide_like();
        } else {
            self.show_like();
        }
    }
    self.hide_like = function () {
        self.heart_el.removeClass("show");
        self.img_el.attr("src", self.heart_img);
    }
    self.show_like = function () {
        self.heart_el.addClass("show");
        self.img_el.attr("src", self.heart_full_img);
    }

    self.add_like = function (opt) {
        if (self.like_l.contains(opt.user)) {
            self.like_l.remove(opt.user);
        } else {
            self.like_l.push(opt.user);
        }
        self.update_like();
    }

    self.init_handlers = function () {
        /* emoji popup */
        if (self.user != fp.user) {
            self.el.on("click", "div.heart", function (e) {
                // send to everyone else
                fp.api.query({
                    'chat.send_like': {
                        thread_id: self.thread.id,
                        message_idx: self.idx,
                    }
                });
            });
        }
    }

    self.init();
}

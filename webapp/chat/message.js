function message (container, thread, config, idx, nest = false) {
    var self = this;
    let append = nest ? "append":"prepend";
    el.call(self, container, append);

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
        if (nest) {
            self.html = self.get_text_html();
        } else {
            self.html = `
                <div class="message_wrapper">`;
            if (self.me) {
                self.html += `<div class="me_bar"></div>`;
            }
            self.html += `
                  <img class="threadpic" src="${self.user.pic_url}">
                  <div class="name">${self.user.full_name}</div>`;
            self.html += self.get_text_html();
            self.html += `</div>`;

        }
        self.add_to_page();

        self.heart_el = self.el.find('div.heart');
        self.seen_el = self.el.find('div.seen');
        self.img_el = self.el.find('div.heart img');

        self.update_like();
        self.init_handlers();
    }

    self.get_text_html = function (text) {
        return `
          <div class="message_sub_wrapper">
            <div class="message">
              ${self.text}
              <div class="timestamp">${self.timestamp}</div>
              <div class="heart ${self.me ? "noclick":""}">
                <img src="${self.heart_img}" />
              </div>
            </div>
          <div class="seen"></div>
          </div>`;
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

    self.add_seen = function (user_id) {
        let user = fp.user_d[user_id];
        let img_url = user.pic_url;
        let name = user.full_name;
        self.seen_el.append(`<div class="seen_bubble">`+
                            `<img id="${user_id}" src="${img_url}">`+
                            `<span>Seen by ${name}</span>`+
                            `</div>`);
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
                return false;
            });
        }
    }

    self.init();
}

function chat_thread (container, id) {
    var self = this;
    el.call(self, container);
    self.message_l = [];
    self.last_user = null;
    self.typing_timeout = 5000;
    self.typing_timer = null;
    self.typing_d = {};

    if (id.includes("=")) {
        self.user = fp.user_d[id.split("=")[1]];
        self.label = self.user.full_name;
        self.user_id = self.user.id;
        self.thread_id = null;
    } else {
        self.thread = fp.thread_d[id];
        self.label = self.thread.label;
        self.user_id = null;
        self.thread_id = id;
    }

    // initialize the thread
    self.init = function () {
        self.html = `
          <div id="thread">
            <div id="label"><span>${self.label}</span></div>
            <div id="thread"></div>
            <div id="thread_input_wrapper">
              <img class="threadpic" src="${fp.user.pic_url}">
              <div id="thread_input" class="textarea" contenteditable>
              </div>
              <div id="emoji">
                <img src="${utility.static_url('img/smile.svg')}" />
              </div>
            </div>
          </div>`;

        self.add_to_page();
        self.thread_el = self.el.find("div#thread");
        self.input_el = self.el.find("div#thread_input");
        self.init_handlers();
    }

    self.init_handlers = function () {

        // add handler for incoming thread history
        fp.api.thread = function (message_l) {
            for (let msg of message_l) {
                self.add_message(msg);
            }
        }

        // get the thread history
        fp.api.query({
            name: "thread",
            options: {
                thread_id: self.thread_id,
                user_id: self.user_id
            }
        });

        // emoji popup
        self.el.on("click", "div#emoji", function (e) {
            var emoji_btn = $(this);
            let pickerOptions = {
                theme: "light",
                onEmojiSelect: console.log,
                previewPosition: "none",
                navPosition: "bottom",
                perLine: 10,
                noCountryFlags: true,
                maxFrequentRows: 1,
                emojiButtonSize: 32,
                emojiSize: 22,
                autoFocus: true,
                onClickOutside: function (e) {
                    $('em-emoji-picker').remove();
                },
                onEmojiSelect: function (e) {
                    $('em-emoji-picker').remove();
                    self.input_el.append(e.native);
                    utility.placeCursorAtEnd(self.input_el.get(0));
                },
            }
            const picker = new EmojiMart.Picker(pickerOptions);
            self.el.find("div#thread_input").append(picker);
            return false;
        });

        self.el.on("keypress", "div#thread_input", function(e) {

        })

        self.el.on("keypress", "div#thread_input", function(e) {
            if (e.which == 13) {
                e.preventDefault();
                let msg = $(this).text();
                if (msg) {
                    let query = {
                        name: 'message',
                        options: {
                            thread_id: self.thread_id,
                            to_user_id: self.user_id,
                            text: msg,
                        }
                    }

                    // send the query
                    fp.api.query(query);

                    $(this).empty();
                }
                return false;
            } else {
                // clear typing timeout
                if (self.typing_timer) {
                    clearTimeout(self.typing_timer);
                } else {
                    // typing notifications
                    fp.api.query({
                        name: 'typing',
                        options: {
                            thread_id: self.thread_id,
                        }
                    });
                }

                self.typing_timer = setTimeout(() => {
                    // typing notifications
                    fp.api.query({
                        name: 'typing',
                        options: {
                            clear: true,
                            thread_id: self.thread_id,
                        }
                    });
                    self.typing_timer = null;
                }, self.typing_timeout);
            }
        })

        fp.api.handlers.message = function (options) {
            if (options.thread == self.thread_id) {
                self.add_message(options.message);
            }
        }
        fp.api.handlers.typing = function (options) {
            if (options.thread == self.thread_id) {
                let user = fp.user_d[options.user];
                let name = user.full_name;
                if (options.clear) {
                    self.typing_d[user.id].remove();
                } else {
                    self.thread_el.prepend(`<div class="divider">`+
                                           `<span>${name} is typing...</span>`+
                                           `</div>`);
                    self.typing_d[user.id] = self.thread_el.children().first();
                }
            }
        }
    }

    self.add_message = function (msg) {
        date = utility.getDateString(msg.timestamp);

        if (date != self.last_date) {
            self.last_user = null;
            self.thread_el.prepend(`<div class="divider timestamp"><span>${date}</span></div>`);
        }
        if (msg.user == self.last_user) {
            let latest = self.message_l.last();
            latest.update(msg);
        } else {
            self.message_l.push(new message (self.thread_el, msg));
        }
        self.thread_el.scrollTop(self.thread_el.prop("scrollHeight"));
        self.last_user = msg.user;
        self.last_date = utility.getDateString(msg.timestamp);
    }

    self.init();
}

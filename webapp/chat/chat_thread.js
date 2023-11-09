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
        self.pic_url = self.user.pic_url;
        self.label = self.user.full_name;
        self.user_id = self.user.id;
        self.id = null;
    } else {
        self.thread = fp.thread_d[id];
        if (self.thread.user) {
            let user = fp.user_d[self.thread.user];
            self.label = user.full_name;
        } else {
            self.label = self.thread.label;
        }
        self.user_id = null;
        self.id = id;
    }

    // initialize the thread
    self.init = function () {
        self.html = `
          <div id="thread">
            <div id="label">
              <span>
                <img class="pic" src="${self.pic_url}">
                ${self.label}
              </span>
            </div>
            <div id="thread"></div>
            <div id="thread_input_wrapper">
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

    // initialize event handlers
    self.init_handlers = function () {

        // add handler for incoming thread history
        fp.api.handlers.thread = function (opt) {
            self.id = opt.id;
            for (let msg of opt.message_l) {
                self.add_message(msg);
            }
        }

        // If we don't have a thread ID, we'll want to wait for one
        if (!self.id) {
            fp.api.handlers.new_thread = function (opt) {
                if (self.user_id == opt.user) {
                    self.id = opt.id
                }
            }
        }

        /* message received */
        fp.api.handlers.message = function (options) {
            if (options.thread == self.id) {
                let user_id = options.message.user;
                // remove the typing indicator
                self.remove_typing(user_id);
                // insert the message to the thread
                self.add_message(options.message, update=true);
            }
        }

        /* typing notification received */
        fp.api.handlers.typing = function (options) {
            let user_id = options.user;
            if (options.thread == self.id) {
                // add or remove typing indicator
                if (options.clear) {
                    self.remove_typing(user_id);
                } else {
                    self.add_typing(user_id);
                }
            }
        }

        fp.api.handlers.like = function (options) {
            if (options.thread == self.id) {
                let message = self.message_l[options.message_idx];
                message.add_like(options);
            }
        }

        // get the thread history
        fp.api.query({
            'chat.get_thread_history': {
                thread_id: self.id,
                user_id: self.user_id
            }
        });

        /* typing in the input */
        self.el.on("keypress", "div#thread_input", function(e) {
            if (e.which == 13) {
                e.preventDefault();
                let msg = $(this).text();
                if (msg) {
                    let query = {
                        'chat.send_message': {
                            thread_id: self.id,
                            user_id: self.user_id,
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
                        'chat.send_typing': {
                            thread_id: self.id,
                        }
                    });
                }

                self.typing_timer = setTimeout(() => {
                    // typing notifications
                    fp.api.query({
                        'chat.send_typing': {
                            clear: true,
                            thread_id: self.id,
                        }
                    });
                    self.typing_timer = null;
                }, self.typing_timeout);
            }
        })

        /* emoji popup */
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

        /* autohide the scroll bar */
        scroll_autohide(self, self.thread_el);
    }

    // add a typing indicator
    self.add_typing = function (user_id) {
        if (!(user_id in self.typing_d)) {
            let user = fp.user_d[user_id];
            let name = user.full_name;
            self.thread_el.prepend(`<div class="divider">`+
                                   `<span>${name} is typing...</span>`+
                                   `</div>`);
            self.scroll_to_end();
            self.typing_d[user_id] = self.thread_el.children().first();
        }
    }

    // remove a typing indicator
    self.remove_typing = function (user_id) {
        if (user_id in self.typing_d) {
            self.typing_d[user_id].remove();
            delete self.typing_d[user_id];
        }
    }

    // add a mesage
    self.add_message = function (msg, update = false) {
        date = utility.getDateString(msg.timestamp);

        if (date != self.last_date) {
            self.last_user = null;
            self.thread_el.prepend(`<div class="divider timestamp"><span>${date}</span></div>`);
        }
        if (msg.user == self.last_user) {
            self.message_l.push(new message (self.latest.el, self, msg, self.message_l.length, true));
        } else {
            self.message_l.push(new message (self.thread_el, self, msg, self.message_l.length));
            self.last_user = msg.user;
            self.latest = self.message_l.last();
        }
        if (update) {
            self.scroll_to_end();
        }
        self.last_date = utility.getDateString(msg.timestamp);
    }

    self.scroll_to_end = function () {
        self.thread_el.scrollTop(self.thread_el.prop("scrollHeight"));
    }

    self.init();
}

function chat_thread (container, id) {
    var self = this;
    el.call(self, container);

    self.message_l = [];
    self.last_user = null;
    self.typing_timeout = 5000;
    self.typing_timer = null;
    self.typing_d = {};
    self.handler = {};

    if (id.includes("=")) {
        // it's a user:user thread
        self.user_id = id.split("=")[1]
        self.user = fp.user_d[self.user_id];
        self.pic_url = self.user.pic_url;
        self.label = self.user.full_name;
        self.thread = fp.user_thread_d[self.user_id];
        if (self.thread) {
            self.id = self.thread.id;
        } else {
            self.id = null;
        }
    } else {
        // it's a group thread
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
              <div id="thread_input_btn">
                ${svg.plus}
              </div>
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
        self.input_el.focus();
        self.init_handlers();
    }

    // initialize event handlers
    self.init_handlers = function () {
        // register with the api
        fp.api.register(self);

        // get the thread history
        if (self.id) {
            fp.api.query({
                'chat.get_thread_history': {
                    thread_id: self.id,
                }
            });
        }

        /* typing in the input */
        self.el.on("keypress", "div#thread_input", function(e) {
            if (e.which == 13) {
                e.preventDefault();
                let msg = $(this).text();
                if (msg) {
                    // send the message over the websocket
                    fp.api.query({
                        'chat.send_message': {
                            thread_id: self.id,
                            user_id: self.user_id,
                            text: msg,
                        }
                    });

                    $(this).empty();
                }
                return false;
            } else if (self.id) {
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

        self.thread_el.on("scroll", function(e) {
            console.log(utility.elInView(self.message_l.last().el));
            return
            for (let msg of self.message_l)  {
                let el = msg.el;
                console.log(utility.elInView(el));
            }
        });
    }

    // add a typing indicator
    self.add_typing = function (user_id) {
        if (!(user_id in self.typing_d)) {
            let user = fp.user_d[user_id];

            // get the name to show
            let name;
            if (self.thread.type == 0) {
                name = user.first_name;
            } else {
                name = user.full_name;
            }

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

    self.seen = function () {
        if (fp.active && self.thread.seen[fp.user.id] < self.message_l.length-1) {
            fp.api.query({
                'chat.send_seen': {
                    thread_id: self.id,
                    message_idx: self.message_l.length-1
                }
            });
        }
    }

    self.update_seen = function () {
        // clear the seen
        self.el.find('.seen').empty();

        for (var uid in self.thread.seen) {
            if (uid != fp.user.id) {
                let seen_idx = self.thread.seen[uid];
                let message = self.message_l[seen_idx];
                message.add_seen(uid);
            }
        }
    }

    self.on_active = function () {
        self.seen();
    }

    /*
     * api handlers
     */

    /* handler for incoming thread history */
    self.handler.thread = function (opt) {
        for (let msg of opt.message_l) {
            self.add_message(msg);
        }
        self.seen();
        self.update_seen();
    }

    /* If we don't have a thread ID, we'll want to wait for one */
    if (!self.id) {
        self.handler.new_thread = function (thread) {
            if (self.user_id == thread.user.id) {
                self.id = thread.id;
            }
        }
    }

    /* message received */
    self.handler.message = function (opt) {
        if (opt.thread == self.id) {
            let user_id = opt.message.user;
            // remove the typing indicator
            self.remove_typing(user_id);
            // insert the message to the thread
            self.add_message(opt.message, update=true);

            // send the message seen notification
            self.seen();
            self.thread.seen[user_id] = self.message_l.length-1;
            self.update_seen();
        }
    }

    /* typing notification received */
    self.handler.typing = function (opt) {
        let user_id = opt.user;
        if (opt.thread == self.id) {
            // add or remove typing indicator
            if (opt.clear) {
                self.remove_typing(user_id);
            } else {
                self.add_typing(user_id);
            }
        }
    }

    /* like received */
    self.handler.like = function (opt) {
        if (opt.thread == self.id) {
            let message = self.message_l[opt.message_idx];
            message.add_like(opt);
        }
    }

    /* seen received */
    self.handler.seen = function (opt) {
        if (opt.thread == self.id) {
            let message = self.message_l[opt.message_idx];
            self.el.find(`img#${opt.user}`).remove();
            message.add_seen(opt.user);
        }
    }

    self.init();
}

function select_users (container, config, append = true) {
    var self = this;
    form_el.call(self, container, config, append);

    self.temp_value = self.value || [fp.user.id];
    self.selected_d = {};

    // initialize the element
    self.init = function () {
        self.html = `
          <div class="select_users_wrapper">
            <label class="form select_users" style="width: ${self.width}">
              ${self.label}${self.asterisk}<br>
              <input type="search" placeholder="Search users..."></input>
              <div id="results_wrapper"></div>
            </label>
            <div id="selected" class="show_scrollbar" hidden></div>
          </div>`;

        self.add_to_page();
        self.label_el = self.el.find('label')
        self.search_el = self.el.find('input')
        self.results_el = self.el.find('div#results_wrapper')
        self.selected_el = self.el.find('div#selected');

        for (let user_id of self.temp_value) {
            if (user_id != fp.user.id) {
                self.add_user(user_id, true);
            }
        }

        self.init_handlers();
    }

    // initialize event handlers
    self.init_handlers = function () {
        /* on search input */
        self.search_el.on("input", function(e) {
            let filter = $(this).val();
            if (filter) {
                new select_users_results (self.results_el, filter, self.temp_value);
            } else {
                self.results_el.empty();
            }
        })

        /* hide the results when clicking out of the search bar */
        self.el.on("focusin focusout", function (e) {
            self.results_el.toggle(e.type == "focusin");
        })
        /* clicking on results shouldn't change focus */
        self.results_el.on("mousedown", function (e) {
            e.preventDefault();
        });

        /* enter pressed */
        self.search_el.on('keypress', function(e) {
            if (e.which == 13) {
                if (self.results_el.find('div.badge').length == 1) {
                    self.results_el.find('div.badge').first().trigger('click');
                }
            }
        })

        /* member clicked */
        self.results_el.on("click", "div.badge", function (e) {
            // find the user id from the element
            let user_id = $(this).attr("id");
            // add user to the selected
            self.add_user(user_id);

            // we're done with the search, clear everything
            self.results_el.empty();
            self.search_el.val("");
        })

        /* member removed */
        self.selected_el.on("click", "span.remove", function (e) {
            // find the user id from the element
            let user_id = $(this).closest('div.badge').attr("id");
            let user = fp.user_d[user_id];
            // remove the element from the page
            self.selected_d[user_id].el.remove();
            // remove the object from our memory
            delete self.selected_d[user_id];
            // remove user from the form value
            self.temp_value.remove(user.id);
            self.update();
        })
    }

    self.add_user = function (user_id, init = false) {
        // find the user object
        let user = fp.user_d[user_id];
        // add the user id to the form value
        if (!init) {
            self.temp_value.push(user.id);
            self.update();
        }
        // add the visual element (and remember it)
        self.selected_d[user.id] = new badge (self.selected_el, user, "selected", append = true);
    }

    // update the input
    self.update = function () {
        if (self.temp_value.length > 1) {
            self.value = self.temp_value;
            self.selected_el.show();
        } else {
            self.value = null;
            self.selected_el.hide();
        }
        self.el.trigger("input");
    }
}

function select_users_results (container, search, exclude) {
    var self = this;
    el.call(self, container);

    self.search = search.toLowerCase();

    // initialize
    self.init = function () {
        self.html = '<div id="results"></div>';
        self.add_to_page();

        let filtered_user_d = fp.filter_users(self.search, true);

        for (let id in filtered_user_d) {
            if (!exclude.includes(id)) {
                let user = filtered_user_d[id];
                new badge (self.el, user, "select", append = true);
            }
        }
    }

    self.init();
}

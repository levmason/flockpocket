function family_row (container, config = {}, index, taken,  append = true) {
    var self = this;
    el.call(self, container, append);

    // init config
    self.user_id = config.user_id;
    self.user = null;
    if (self.user_id) {
        self.user = fp.user_d[self.user_id]
        self.name = `${self.user.full_name} (${self.user.email})`;
    } else {
        self.name = config.name || "";
    }
    self.taken = taken || [];
    self.type = config.type || "";

    self.disabled = self.name ? "":"disabled";
    self.index = index;
    self.value = config.value || "";

    self.rel_d = {
        'Husband': {
            gender: "Male",
            required_gender: "Female",
            unique: true,
        },
        'Wife': {
            gender: "Female",
            required_gender: "Male",
            unique: true,
        },
        'Son': {
            gender: "Male",
        },
        'Daughter': {
            gender: "Female",
        },
        'Brother': {
            gender: "Male",
        },
        'Sister': {
            gender: "Female",
        },
        'Mother': {
            gender: "Female",
            unique: true,
        },
        'Father': {
            gender: "Male",
            unique: true,
        },
        'Grandmother': {
            gender: "Female",
        },
        'Grandfather': {
            gender: "Male",
        }
    }

    // initialize the element
    self.init = function () {
        self.html = `
          <tr index=${self.index}><td>
            <input value="${self.name}" />
            <div class="results"></div>
          </td>
          <td>
          <select ${self.disabled}>`;

        self.html += `</select></td></tr>`;

        self.add_to_page();
        self.results_el = self.el.find("div.results");
        self.type_el = self.el.find("select");
        self.input_el = self.el.find("input");
        self.init_handlers();
        if (self.name) {
            self.set_type_options();
        }
    }

    self.set_type_options = function () {
        let html = "";

        let rel_l = self.get_type_options();

        for (var rel of rel_l) {
            let selected = (self.type == rel) ? "selected":"";
            html += `<option value="${rel}" ${selected}>${rel}</option>`;
        }

        if (self.type) {
            self.taken.add(self.type);
        }

        self.type_el.html(html);

    }

    self.get_type_options = function () {
        let my_gender = fp.user.gender;

        rel_l = [''];
        for (var rel_type in self.rel_d) {
            let rel_type_details = self.rel_d[rel_type];
            // make sure we're the right gender
            if (rel_type_details.required_gender && fp.user.gender != rel_type_details.required_gender) {
                continue;
            }

            // make sure this isn't a unique relationship that's already set
            if (self.type != rel_type && rel_type_details.unique && self.taken.has(rel_type)) {
                continue;
            }

            if (self.user) {
                // make sure the type has the right gender
                if (rel_type_details.gender && self.user.gender != rel_type_details.gender) {
                    continue;
                }
            }
            rel_l.push(rel_type);
        }

        return rel_l;
    }

    // initialize handlers
    self.init_handlers = function () {

        /* save name value */
        self.input_el.on("input", function (e) {
            self.name = $(this).val();
            self.user = self.user_id = null;

            let idx = $(this).closest("tr").attr("index");

            /* enable the relationship selector */
            self.type_el.prop("disabled", !Boolean(self.name));

            /* show the search results */
            if (self.name) {
                /* add the type options */
                //self.set_type_options();
                self.results_el.empty().show();
                let filtered_user_d = fp.filter_users(self.name, false);
                for (let id in filtered_user_d) {
                    let user = filtered_user_d[id];
                    new badge (self.results_el, user, "family", append = true);
                }
            } else {
                self.results_el.hide();
            }
        })

        /* member clicked */
        self.results_el.on("click", "div.badge", function (e) {
            self.user_id = $(this).attr("id");
            self.user = fp.user_d[self.user_id];

            // store the results
            self.input_el.val(`${self.user.full_name} (${self.user.email})`);
            $(this).trigger("input");

            // we're done with the search
            self.results_el.hide();

            // update the type selector
            self.set_type_options();
        })

        /* type selected */
        self.type_el.on("input", function (e) {
            // remove from the taken relationships
            if (self.type) {
                self.taken.delete(self.type);
            }
            self.type = $(this).val();
            // add to the taken relationships
            if (self.type) {
                self.taken.add(self.type);
            }
            $(this).toggleClass("error", !Boolean(self.type))
        })
    }

    self.init();
}

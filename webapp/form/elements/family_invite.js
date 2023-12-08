function family_invite (container, config = {}, append = true) {
    var self = this;
    form_el.call(self, container, config, append);

    // initialize the badge
    self.init = function () {
        self.options = self.relationship_options();

        self.html = `
          <label class="form" style="width: ${self.width}">
            ${self.label}${self.asterisk}<br>
            <select name="${self.id}">`;

        for (let opt of self.options) {
            let selected = "";
            if (opt.indexOf('[') == 0) {
                let label = opt.replace('[', "").replace(']', "");
                self.html += `<optgroup label="${label}">`;
                //self.html += `<option disabled>${label}</option>`;
                continue;
            }
            if (opt == self.value) {
                selected = "selected";
            }
            self.html += `<option value="${opt}" ${selected}>${opt}</option>`;
        }
        self.html += '</label>';

        self.add_to_page();
        self.init_handlers();
    }

    self.relationship_options = function () {
        let user_l = [''];
        for (let member of fp.user.family) {
            if (!member.user_id) {
                let username = member.name;
                user_l.push(`${member.type} (${username})`);
            }
        }
        user_l.push("[New]");
        user_l = utility.merge(user_l, fp.user.possible_relationships());
        return user_l;
    }

    // initialize handlers
    self.init_handlers = function () {
        /* save value */
        self.el.on("input", function (e) {
            let val = self.el.find('select').val();
            if (val.includes('(')) {
                let [type, name] = val.match(/(\w+) \(([\w\s]+)\)/).slice(1,3);
                self.value = {
                    type: type,
                    name: name,
                }
            } else {
                self.value = {
                    type: val
                }
            }
        })
    }
}

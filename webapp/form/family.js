function family (container, config = {}, append = true) {
    var self = this;
    form_el.call(self, container, config, append);

    self.value_draft = utility.deep_copy(self.value) || [];
    self.value_draft.push({});
    self.taken = new Set();
    self.row_l = [];

    // initialize the element
    self.init = function () {

        self.html = `
          <table id="family_members" class="form ${self.hidden}" page="${self.page}">
            <thead><tr><th>Name</th><th>Relationship</th></tr></thead>`;

        self.html += '</table>';

        self.add_to_page();
        self.init_handlers();

        // add the rows
        for (let usr of self.value_draft) {
            if (!usr.user_id || fp.user_d[usr.user_id]) {
                self.row_l.push(new family_row(self.el, usr, self.row_l.length, self.taken, true));
            }
        }
    }

    // initialize handlers
    self.init_handlers = function () {

        self.el.on("input", function () {
            self.value = [];
            for (let row of self.row_l) {
                row.set_type_options();
                if (row.name && row.type) {
                    self.value.push({
                        name: row.name,
                        type: row.type,
                        user_id: row.user_id,
                    })
                }
            }

            if (self.value.length == self.row_l.length) {
                self.row_l.push(new family_row(self.el, {}, self.row_l.length, self.taken, true))
            }
        });
    }
}

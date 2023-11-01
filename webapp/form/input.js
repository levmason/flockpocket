function input (container, config = {}, append = true) {
    var self = this;
    form_el.call(self, container, config, append);

    // initialize the element
    self.init = function () {
        let placeholder_str = self.placeholder ? `placeholder="${self.placeholder}"` : "";

        self.html = `
          <label class="form ${self.hidden}" style="width: ${self.width}" page="${self.page}">
            ${self.label}${self.asterisk}
            <input ${placeholder_str} name="${self.id}" value="${self.value}" />
          </label>`;

        self.add_to_page();
        self.init_handlers();
    }

    // initialize handlers
    self.init_handlers = function () {
        /* save value */
        self.el.on("input", function (e) {
            self.value = self.el.find('input').val();
            if (!self.value && self.starting_value) {
                self.value = self.starting_value;
            }
        })
    }
}

function select (container, config = {}, append = true) {
    var self = this;
    form_el.call(self, container, config, append);

    // initialize config
    if (typeof config.options === 'function') {
        self.options = config.options();
    } else {
        self.options = config.options;
    }

    // initialize the badge
    self.init = function () {
        self.html = `
          <label class="form" style="width: ${self.width}">
            ${self.label}${self.asterisk}<br>
            <select name="${self.id}">`;

        for (let opt of self.options) {
            let selected = "";
            if (opt == self.value) {
                selected = "selected";
            }
            self.html += `<option value="${opt}" ${selected}>${opt}</option>`;
        }
        self.html += '</label>';

        self.add_to_page();
        self.init_handlers();
    }

    // initialize handlers
    self.init_handlers = function () {
        /* save value */
        self.el.on("input", function (e) {
            self.value = self.el.find('select').val();
        })
    }
}

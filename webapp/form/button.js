function button (container, config = {}, append = false) {
    var self = this;
    form_el.call(self, container, config, append);

    // read options
    self.disabled = config.disabled ? "disabled" : "";

    // initialize
    self.init = function () {
        self.html += `<button id="${self.id}" class="big ${self.hidden}"`+
            `${self.disabled}>${self.label}</button>`;

        // add to the page
        self.add_to_page();
    }

    self.init();
}

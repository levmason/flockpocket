function text (container, config = {}, append = true) {
    var self = this;
    // set defaults
    config.width = config.width || "100%";
    form_el.call(self, container, config, append);

    // read options
    self.list = config.list || false;

    // initialize the element
    self.init = function () {
        let starting_value = self.value;
        if (starting_value && self.list) {
            try {
                starting_value = self.value.join("\n");
            } catch {}
        }

        self.html = `
          <label class="form ${self.hidden}" style="width: ${self.width}" page="${self.page}">
            ${self.label}${self.asterisk}<br>
            <div class="textarea" id="${self.id}" contenteditable>${starting_value}</div>
          </label>`;

        self.add_to_page();
        self.init_handlers();
    }

    // initialize handlers
    self.init_handlers = function () {
        /* save value */
        self.el.on("input", function (e) {
            let val = self.el.find('div').text();
            if (self.list) {
                val = val.split(/\r?\n/).filter(n => n);
            }
            self.value = val;
        })

        /* pasting into contenteditable div requires special handling :/ */
        self.el.on("paste", "div.textarea", function (e) {
            e.preventDefault();
            var text = e.originalEvent.clipboardData.getData('text/plain');
            $(this).text(text);
            utility.placeCursorAtEnd(this);
            $(this).trigger("input");
        })
    }
}

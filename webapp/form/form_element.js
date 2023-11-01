function form_el (container, config, append) {
    var self = this;
    el.call(self, container, append);

    // read config
    self.label = config.label || "";
    self.id = config.id || self.label.lower().replace(/ /g,"_");
    self.width = config.width || "50%";
    self.width = `calc(${self.width} - 28px)`;
    self.hidden = config.hidden ? "hidden":"";
    self.required = config.required || false;
    self.asterisk = self.required ? "*":"";
    self.placeholder = config.placeholder || "";
    self.value = config.value || "";
    self.page = config.page || 1;

    if (self.required && self.value) {
        self.starting_value = self.placeholder = self.value;
        self.asterisk = "";
    }
}


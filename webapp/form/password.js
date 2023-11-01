function password (container, config = {}, append = true) {
    var self = this;
    form_el.call(self, container, config, append);

    // init config
    self.label = config.label || "Password";

    // initialize the element
    self.init = function () {
        self.html = `<span><label class="form" style="width: ${self.width}">`+
            `${self.label}${self.asterisk}`+
            `<br><input type="password" name="${self.id}" /></label>`+
            `<label class="form" style="width: ${self.width}">`+
            `Confirm ${self.label}${self.asterisk}`+
            `<br><input type="password" name="${self.id}" /></label></span>`;

        self.add_to_page();
        self.init_handlers();
    }

    // initialize handlers
    self.init_handlers = function () {
        /* watch for input */
        self.el.on("input", function (e) {
            let valid = self.validate()
            // underline red
            if (valid) {
                self.value = self.el.find('input').val();
                $('input', self.el).removeClass("error");
            } else {
                self.value = "";
                $('input', self.el).addClass("error");
            }
        })
    }

    // validate the input
    self.validate = function () {
        var pw_l = [];
        $('input:password', self.el).each(function() {
            pw_l.push($(this).val());
        })
        return Boolean(pw_l[0] != "" && pw_l[0] == pw_l[1]);
    }
}

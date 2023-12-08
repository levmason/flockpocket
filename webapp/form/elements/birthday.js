function birthday (container, config = {}, append = true) {
    var self = this;
    input.call(self, container, config, append);

    // initialize the config
    self.placeholder = self.placeholder || "xx/xx/xxxx";

    // initialize handlers
    self.init_handlers = function () {
        /* save the value */
        self.el.on("input", "input", function(e) {
            let val = $(this).val().replace(/[^\d]/g, '');

            // trim to 10
            if (val.length > 8) {
                val = val.slice(0,8);
            }

            // add dashes
            if (val.length > 4) {
                val = val.slice(0,2) + '/' + val.slice(2,4) + '/' + val.slice(4);
            } else if (val.length > 2) {
                val = val.slice(0,2) + '/' + val.slice(2);
            }

            $(this).val(val);

            let valid = self.validate(val);

            // underline red
            if (valid) {
                self.value = self.el.find('input').val();
                $('input', self.el).removeClass("error");
            } else {
                self.value = "";
                $('input', self.el).addClass("error");
            }
        });
    }

    // validate the input
    self.validate = function (val) {
        val = val.replace(/[^\d]/g, '');
        return Boolean(val.length == 8);
    }
}

function phone (container, config = {}, append = true) {
    var self = this;
    input.call(self, container, config, append);

    // initialize the config
    self.placeholder = self.placeholder || "xxx-xxx-xxxx";

    // initialize handlers
    self.init_handlers = function () {
        self.el.on("input", "input", function(e) {
            let val = $(this).val().replace(/[^\d]/g, '');

            // remove the 1
            if (val.startsWith('1')) {
                val = val.slice(1);
            }

            // trim to 10
            if (val.length > 10) {
                val = val.slice(0,10);
            }

            // add dashes
            if (val.length > 6) {
                val = val.slice(0,3) + '-' + val.slice(3,6) + '-' + val.slice(6);
            } else if (val.length > 3) {
                val = val.slice(0,3) + '-' + val.slice(3);
            }

            $(this).val(val);

            let valid = self.validate(val);

            // underline red
            if (!val && self.starting_value) {
                self.value = self.starting_value;
                $('input', self.el).removeClass("error");
            } else if (valid) {
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
        return Boolean(val.length == 10);
    }
}

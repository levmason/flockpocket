function form (container, config, append = false) {
    var self = this;
    el.call(self, container, append);

    self.inputs = config.inputs;
    self.handler = config.handler;
    self.message = config.message;
    self.btn_label = config.btn_label || "Submit";
    self.page = 1;
    self.page_count = 1;
    self.wait_text = config.wait_text || "Please wait...";
    self.valid = false;
    self.form_l = [];

    // initialize
    self.init = function () {
        // add the title
        if (config.title) {
            self.html += '<h1>'+config.title+'</h1>';
        }

        self.html += '<div class="form"></div>';

        self.add_to_page();
        self.init_handlers();

        /* add form elements */
        for (let x of self.inputs) {
            x.hidden = Boolean(self.page != self.page_count) ? "hidden":"";
            x.page = self.page_count;

            switch (x.type) {
            case "help":
                self.el.append(`<div class="form card ${x.hidden}" page="${x.page}">${x.message}</div>`);
                break;
            case "divider":
                self.el.append(`<div class="form divider ${x.hidden}" page="${x.page}">`+
                               `<span>${x.label}</span></div>`);
                break;
            case "break":
                self.page_count++;
                break;
            default:
                var el_constructor = (eval(x.type));
                var el = new el_constructor(self.el, x, true);
                el.init();
                self.form_l.push(el);
            }
        }

        self.el.append("<br>");

        /* add buttons */
        let buttons = [];

        // next/back
        if (self.page_count > 1) {
            buttons.push({
                label: "Back",
                hidden: "hidden",
            })
            buttons.push({
                label: "Next",
                hidden: "",
                disabled: true,
            })
        }

        // submit
        buttons.push({
            label: self.btn_label,
            id: "submit",
            disabled: true,
            hidden: self.page_count > 1 ? "hidden" : ""
        });

        for (let btn of buttons) {
            new button (self.el, btn, true);
        }
    }

    // initialize handlers
    self.init_handlers = function () {
        /* verify that required inputs are there */
        self.el.on("input", function (e) {
            self.validate();
        });

        /* next button click */
        self.el.on("click", "button#next", function (e) {
            self.page++;
            self.update();
        })

        /* back button click */
        self.el.on("click", "button#back", function (e) {
            self.page--;
            self.update()
        })

        /* submit the new user */
        self.el.on("click", "button#submit", function (e) {
            utility.blockUI(self.wait_text);
            self.handler(function() {
                $('#content').html('<div class="form_submitted">'+self.message+'</div>')
                $.unblockUI();
            });
        })
    }

    // validate the input
    self.validate = function () {
        self.valid = true;
        for (let el of self.form_l) {
            if (el.required && !el.value) {
                self.valid = false;
                break;
            }
        }

        $('button#submit, button#next').prop("disabled", !self.valid);
    }

    // get the form value as an object
    self.value = function () {
        var res_l = {};
        for (let el of self.form_l) {
            if (el.value) {
                res_l[el.id] = el.value;
            }
        }
        return res_l;
    }

    // update the form (hidden elements etc)
    self.update = function () {
        // hide/show elements
        $('.form[page='+self.page+']', self.el).removeClass("hidden");
        $('.form[page!='+self.page+']', self.el).addClass("hidden");

        // hide/show buttons
        $('button#back', self.el).toggleClass("hidden", self.page == 1);
        $('button#next', self.el).toggleClass("hidden", self.page == self.page_count);
        $('button#submit', self.el).toggleClass("hidden", self.page < self.page_count);
    }

    self.init();
    self.validate();
}

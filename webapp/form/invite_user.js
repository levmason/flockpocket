function invite_user (container, append = false) {
    var self = this;
    el.call(self, container, append);

    self.form = null;
    self.form_cfg = {
        title: "Invite a New User",
        btn_label: "Send",
        message: "Invite sent!",
        handler: function (callback) {
            let value = self.form.value();
            let data = {data: JSON.stringify(value)};
            let url = utility.api_url("invite_user");

            $.post(url, data)
                .fail(function(response, status) {
                    $.unblockUI();
                    modal.alert("User already exists!");
                })
                .done(function(response, status) {
                    callback();
                })
        },
        inputs: [
            {
                type: "input",
                label: "Email",
                width: "60%",
                required: true,
            },
            {
                type: "input",
                label: "First Name",
                width: "60%",
                required: true,
            },
            {
                type: "input",
                label: "Last Name",
                width: "60%",
                required: true,
            },
        ]
    }

    // initialize
    self.init = function () {
        self.form = new form (self.container, self.form_cfg);
    }

    self.init();
}

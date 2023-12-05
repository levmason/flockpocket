function invite_user (container, append = false) {
    var self = this;
    el.call(self, container, append);

    self.form = null;
    self.form_cfg = {
        title: "Create an invite link",
        message: "Invite sent!",
        btn_label: "Create Invite",
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
                    self.link = window.location.origin + root + response.link;
                    self.done();
                })
        },
        inputs: [
            {
                type: "help",
                message: "Provide an email address if you'd like to send an invite email.",
            },
            {
                type: "input",
                label: "(optional) Email",
                //placeholder: "Optional",
                width: "60%",
            },
            {
                type: "select",
                label: "(optional) Household Link",
                //placeholder: "Optional",
                options: ['Male', 'Female'],
                width: "60%",
            },
        ]
    }

    // initialize
    self.init = function () {
        self.form = new form (self.container, self.form_cfg);
    }

    self.done = function () {
        let html = `<div class="form_submitted">Invite sent!</div>
                    <div id="invite_sent">Share this link...<br><a href="${self.link}">${self.link}</a></div>`;
        $('#content').html(html);
        $.unblockUI();
    }

    self.init();
}

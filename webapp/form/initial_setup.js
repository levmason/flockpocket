function initial_setup (container, append = false) {
    var self = this;
    el.call(self, container, append);

    self.form = null;
    self.form_cfg = {
        title: "Complete your Profile...",
        message: "Thank you!",
        btn_label: "Done",
        handler: function (callback) {
            let value = self.form.value();
            console.log(value);
            let data = {details: JSON.stringify(value)};
            let url = utility.api_url("update_user", fp.user.id);

            $.post(url, data)
                .fail(function(response, status) {
                    $.unblockUI();
                })
                .done(function(response, status) {
                    callback();
                })
        },
        inputs: [
            {
                type: "help",
                message: "Welcome to our flock! There are a few more <b>optional</b> steps to complete your profile..."
            },
            {
                type: 'divider',
                label: 'Personal Information',
            },
            {
                type: 'help',
                message: "You can provide some more information about yourself below. This information will appear on your profile when others search for you.",
            },
            {
                type: "text",
                list: true,
                label: "Occupations / Skills / Passions (one per line)",
                id: "skills",
                width: "100%",
                value: user.skills,
            },
            {
                type: "text",
                label: "About Me",
                id: "about",
                width: "100%",
                value: user.about,
            },
            {
                type: "break",
            },
            {
                type: 'divider',
                label: 'Family Members',
            },
            {
                type: "help",
                message: "Adding family members will help to others to understand your household. If you add children, other users will be able to search for them and find your account. If children create accounts, then parents will always be able to access those accounts.",
            },
            {
                type: "family",
                label: "Family Members",
                id: "family",
                width: "100%",
            },
        ]
    }

    // initialize
    self.init = function () {
        // add to the page
        self.form = new form (self.container, self.form_cfg);
    }

    self.init();
}

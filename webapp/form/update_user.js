function user_settings (container, id, append = false) {
    var self = this;
    self.container = container;
    self.el = null;
    self.html = "";
    self.user_id = id;
    self.form = null;
    self.form_cfg = {
        message: "Your request has been submitted!",
        handler: function (callback) {
            let value = self.form.value();
            let pic = value.profile_picture;
            delete value.profile_picture;
            console.log(value);

            var fd = new FormData();
            fd.append("profile_picture", pic);
            fd.append("details", JSON.stringify(value));

            let url = utility.api_url("user_activate");
            $.ajax({
                url: url,
                data: fd,
                processData: false,
                contentType: false,
                type: 'POST',
                success: function(data){
                    callback();
                },
                error: function (request, status, error) {
                    $.unblockUI();
                    modal.alert(request.responseText);
                }
            });
        },
        inputs: [
            {
                type: "profile_pic_uploader",
                label: "Profile Picture"
            },
            {
                type: "input",
                label: "Email",
                width: "50%",
                required: true,
            },
            {
                type: "select",
                label: "Church Membership Status",
                id: 'membership_status',
                width: "50%",
                required: true,
                options: ['Member', 'Regular Attender']
            },
            {
                type: "password",
                label: "Password",
                width: '50%',
                required: true,
            },
            {
                type: "input",
                label: "First Name",
                required: true,
            },
            {
                type: "input",
                label: "Last Name",
                required: true,
            },
            {
                type: "input",
                label: "Home Address",
                id: "address",
                width: "50%",
                required: true,
            },
            {
                type: "input",
                label: "City",
                width: "50%",
                required: true,
            },
            {
                type: "select",
                label: "State",
                width: "50%",
                required: true,
                options: [
                    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
	            "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
                    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
                    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
                    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
                ]
            },
            {
                type: "phone",
                label: "Phone Number",
                id: "phone",
                width: "50%",
                required: true,
            },
            {
                type: "select",
                label: "Gender",
                width: "50%",
                required: true,
                options: ['Male', 'Female'],
            },
            {
                type: "birthday",
                label: "Birthday",
                width: "50%",
                required: true,
            },
            {
                type: "text",
                list: true,
                label: "Occupations / Skills / Passions (one per line)",
                id: "skills",
                width: "100%",
            },
            {
                type: "text",
                label: "About Me",
                id: "about",
                width: "100%",
            }
        ]
    }

    // initialize
    self.init = function () {
        self.html += '<h1>New User Sign-up</h1>';

        // add to the page
        if (self.container) {
            if (append) {
                self.container.append(self.html);
            } else {
                self.container.html(self.html);
            }
            self.el = self.container.children().last();
        }
        self.form = new form (self.container, self.form_cfg, true);
    }

    self.init();
}

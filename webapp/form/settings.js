function settings (container, append = false) {
    var self = this;
    el.call(self, container, append);

    self.form = null;
    self.form_cfg = {
        title: "Edit Profile",
        message: "Your request has been submitted!",
        wait_text: "Saving...",
        btn_label: "Save",
        handler: function (callback) {
            let value = self.form.value();
            let pic = value.profile_picture;
            delete value.profile_picture;

            var fd = new FormData();
            fd.append("profile_picture", pic);
            fd.append("details", JSON.stringify(value));

            let url = utility.api_url("update_user", fp.user.id);
            $.ajax({
                url: url,
                data: fd,
                processData: false,
                contentType: false,
                type: 'POST',
                success: function(data){
                    utility.unblockUI();
                }
            });
        },
        inputs: [
            {
                type: "profile_pic_uploader",
                label: "Profile Picture",
                value: fp.user.pic,
            },
            {
                type: "help",
                message: "Your profile picture should help identify you. Please use a picture of your face!",
            },
            {
                type: "divider",
                label: "Basic"
            },
            {
                type: "help",
                message: "This is required contact/directory information.",
            },
            {
                type: "input",
                label: "Email",
                width: "50%",
                required: true,
                value: fp.user.email,
            },
            {
                type: "select",
                label: "Church Membership Status",
                id: 'membership_status',
                width: "50%",
                required: true,
                options: ['Member', 'Regular Attender'],
                value: fp.user.membership_status
            },
            {
                type: "input",
                label: "First Name",
                required: true,
                value: fp.user.first_name,
            },
            {
                type: "input",
                label: "Last Name",
                required: true,
                value: fp.user.last_name,
            },
            {
                type: "input",
                label: "Home Address",
                id: "address",
                width: "50%",
                required: true,
                value: fp.user.address,
            },
            {
                type: "phone",
                label: "Phone Number",
                id: "phone",
                width: "50%",
                required: true,
                value: fp.user.phone,
            },
            {
                type: "select",
                label: "Gender",
                width: "50%",
                required: true,
                options: ['Male', 'Female'],
                value: fp.user.gender,
            },
            {
                type: "birthday",
                label: "Birthday",
                width: "50%",
                required: true,
                value: fp.user.birthday,
            },
            {
                type: "divider",
                label: "About Me"
            },
            {
                type: "help",
                message: "Here you can add a bit more information about yourself.",
            },
            {
                type: "text",
                list: true,
                label: "Occupations / Skills / Passions (one per line)",
                id: "skills",
                width: "100%",
                value: fp.user.skills,
            },
            {
                type: "text",
                label: "About Me",
                id: "about",
                width: "100%",
                value: fp.user.about,
            },
            {
                type: "divider",
                label: "Family",
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
                value: fp.user.family,
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

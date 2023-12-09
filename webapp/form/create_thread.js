function create_thread () {
    var self = this;
    // create the modal container
    modal.open(`<div id="create_thread"></div>`);
    let container = $(`div#create_thread`);

    el.call(self, container, true);

    self.form_cfg = {
        title: "Create a new thread",
        btn_label: "Create",
        handler: function (callback) {
            let value = self.form.value();
            let data = {data: JSON.stringify(value)};
            let url = utility.api_url("create_thread");

            $.post(url, data)
                .fail(function(response, status) {
                    $.unblockUI();
                    modal.alert("Error creating thread!");
                })
                .done(function(response, status) {
                    self.done(response);
                })
        },
        inputs: [
            {
                type: "input",
                label: "Thread Label",
                placeholder: "Give a label to describe this thread",
                required: true,
                width: "100%",
            },
            {
                type: "select_users",
                required: true,
                label: "Thread Members",
                width: "100%",
            },
        ]
    }

    // initialize
    self.init = function () {
        self.form = new form (self.container, self.form_cfg);
    }

    self.done = function () {
        console.log(response);
        $.unblockUI();
    }

    self.init();
}

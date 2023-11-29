function create_thread () {
    var self = this;

    // create the modal container
    modal.open(`<div id="create_thread"></div>`);
    let container = $(`div#create_thread`);

    el.call(self, container, true);

    self.init = function () {

        self.html = `hello`;
    }

    self.init()
}

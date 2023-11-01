function infocard (container, label, text, append = true) {
    var self = this;
    self.container = container;
    self.el = null;
    self.html = "";

    // initialize the badge
    self.init = function () {
        self.html = '<div class="card">'+
            '<div class="label">' + label  + '</div>';
        if (text) {
            self.html += '<div class="text">' + text + '</div>';
        }

        if (append) {
            self.container.append(self.html);
        } else {
            self.container.html(self.html);
        }
        self.el = self.container.children().last();
    }

    self.init();
}

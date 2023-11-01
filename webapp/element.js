function el (container, append = false) {
    var self = this;
    self.container = container;
    self.el = null;
    self.html = "";

    self.add_to_page = function () {
        // format the string (removing unwanted whitespace)
        self.html = self.html.replace(/\s*\n\s+/g,'');

        // add to the page
        if (self.container) {
            if (append == "prepend") {
                self.container.prepend(self.html);
                self.el = self.container.children().first();
            } else if (append) {
                self.container.append(self.html);
                self.el = self.container.children().last();
            } else {
                self.container.html(self.html);
                self.el = self.container.children().last();
            }
        }
    }
}

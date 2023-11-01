function directory (container) {
    var self = this;
    self.container = container;
    self.el = null;
    self.html = "";

    // initialize
    self.init = function () {
        self.html += '<div id="directory">'+
            '<h1>Directory</h1>'+
            '<input type="search" placeholder="Search..."></input>'+
            '<div id="results"></div>'+
            '</div>';
        self.container.html(self.html);
        self.search_el = self.container.find('input')
        self.results_el = self.container.find('div#results')

    }

    self.init();

    self.search_el.on("input", function(e) {
        let filter = $(this).val();
        if (filter) {
            new results (self.results_el, filter);
        } else {
            self.results_el.empty();
        }
    })
}

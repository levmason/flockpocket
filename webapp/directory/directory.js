function directory (container) {
    var self = this;
    el.call(self, container);

    // initialize
    self.init = function () {
        self.html += '<div id="directory">'+
            '<h1>Directory</h1>'+
            '<input type="search" placeholder="Search..."></input>'+
            '<div id="results"></div>'+
            '</div>';

        self.add_to_page();
        self.search_el = self.container.find('input')
        self.results_el = self.container.find('div#results')

        self.init_handlers();
    }

    self.init_handlers = function () {
        /* on search input */
        self.search_el.on("input", function(e) {
            let filter = $(this).val();
            if (filter) {
                new results (self.results_el, filter);
            } else {
                self.results_el.empty();
            }
        })
    }

    self.init();

}

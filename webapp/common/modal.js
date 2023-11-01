function Modal (options) {
    var self = utility.merge(this, options);
    self.modal_selector = "div.modal#modal"+self.index;
    self.overlay_selector = "div.modal-overlay#modal"+self.index;

    self.init = function() {
        var html = "";

        // add the overlay
        html += '<div class="modal" id="modal'+self.index+'" hidden>'+
            self.content+
            '</div>'+
            '<div class="modal-overlay" id="modal'+self.index+'">'+
            '</div>';

        $('body').append(html);

        self.modal_element = $(self.modal_selector);
        self.overlay_element = $(self.overlay_selector);

        self.modal_element
            .css({
                'width': self.width,
                'min-width': self.minWidth,
                'max-width': self.maxWidth,
                'height': self.height,
                'min-height': self.minHeight,
                'max-height': self.maxHeight,
                'overflow': self.overflow,
                'padding': self.padding,
            })
            .show();

        /* afterShow handler */
        if (self.afterShow) {
            self.afterShow(self);
        }

        /* add the event handlers */
        self.overlay_element.on('click', function() {
            self.close();
        })
    }

    self.close = function() {
        /* remove from modal stack */
        modal.stack.pop();

        /* remove the elements */
        self.overlay_element.remove();
        self.modal_element.remove();

        /* afterClose handler */
        if (self.afterClose) {
            self.afterClose(self);
        }
    }

    self.init();

    return self;
}


modal = {};
// track all of the modal entries
modal.stack = []

/* create a new modal */
modal.open = function (html, options) {
    // default options
    var defaults = {
        content     : html,
        minWidth    : 250,
        minHeight   : 20,
        maxHeight   : "calc(100vh - 100px)",
        overflow: 'visible',
        padding: "15px",
        index: modal.stack.length,
    }

    // merge options with defaults
    options = $.extend({}, defaults, options);

    // map aliases
    if (options.scrolling == "yes") {
        options.overflow = 'scroll';
    }

    let mdl = new Modal(options)
    modal.stack.push(mdl);

    return mdl;
}

/* close the top modal window */
modal.close = function () {
    modal.stack.last().close();
}

/* close all modal windows */
modal.closeAll = function () {
    var length = modal.stack.length;
    for (var i = 0; i < length; i++) {
        modal.stack.last().close();
    }
}

/* confirmation popup */
modal.confirm = function (msg, yes_callback, no_callback) {
    msg = msg || "Are you sure?";
    var ret;

    var html = '' +
        '<table class="popup_table borderless">'+
        '<tr><td colspan=2>'+msg+'</td></tr>'+
        '<tr>'+
        '<td style="padding-top: 5px">'+
        '<button id="confirm_no_btn" class="std_button" style="width: 100px">No</button>'+
        '<button id="confirm_yes_btn" class="std_button" style="width: 100px">Yes</button></td>'+
        '</tr></table>';

    modal.open(html, {
        afterShow: function(self) {
            ret = false;
            $('#confirm_no_btn, #confirm_yes_btn').on("click tap", function(e) {
                ret = (e.target.id == "confirm_yes_btn");
                self.close();
            });
        },
        afterClose: function(self) {
            if (ret && yes_callback) {
                yes_callback.call(this);
            } else if (!ret && no_callback) {
                no_callback.call(this)
            }
        },
    });
}

/* alert popup */
modal.alert = function (msg, callback) {
    var ret;
    var after_fn;

    var html = '' +
        '<table class="popup_table borderless">'+
        '<tr><td colspan=2>'+msg+'</td></tr>'+
        '<tr><td style="padding-top: 5px;">'+
        '<button id="popup_ok_btn" class="std_button" style="width: 100px">OK</button></td>'+
        '</tr></table>';

    if (callback) {
        after_fn = function(self) {
            callback.call(this);
        }
    }

    modal.open(html, {
        afterShow: function(self) {
            ret = false;
            $('#popup_ok_btn', self.modal_element).on("click tap", function(e) {
                self.close();
            });
        },
        afterClose: after_fn,
    });
}

/* widget popup */
modal.widget = function (widget_cfg) {

    // augment the widget config with sizing optinos
    widget_cfg = utility.merge(widget_cfg, {
        width: "100%",
        height: "100%",
    })

    // initialize the dashboard config
    var dashboard_config = {
        widgets: {
            widget: widget_cfg
        }
    };

    let mdl = modal.open('<div id="widget_popup"></div>', {
        padding: 0,
        overflow: "hidden",
        maxHeight: "600px",
        width: "calc(100vw - 150px)",
        height: "calc(100vh - 150px)",
        afterClose: function (self) {
            self.dashboard.close();
        }
    });

    mdl.dashboard = new Dashboard('div.modal#modal'+mdl.index+' #widget_popup', dashboard_config, {});
}

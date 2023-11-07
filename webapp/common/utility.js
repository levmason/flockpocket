/*
 * This file contains "utility" functions.
 * These are any functions that are generally useful and NOT Syfter specific.
 * Syfter general functions should go in syfter.lib.js.
 */

utility = {};

/* Create a python editor textbox (using codemirror) */
utility.python_editor = function (el) {
    let placeholder = $(el).attr('placeholder');
    if (placeholder && !$(el).val()) {
        $(el).val(placeholder);
    }
    let cm = CodeMirror.fromTextArea(el, {
        lineNumbers: true,
        mode: "python",
        smartIndent: false,
        indentUnit: 4,
        matchBrackets: true,
        inputStyle: "contenteditable",
        extraKeys: {
            Tab: function(cm) {
                if (!cm.getSelection().length) {
                    cm.replaceSelection(" ".repeat(cm.getOption("indentUnit")));
                } else {
                    return CodeMirror.Pass;
                }
            },
            Enter: function(cm) {
                return cm.replaceSelection("\n");
            }
        }
    });
    let wrapper = $(cm.getWrapperElement());
    // cm.on("focus", function(cm, e) {
    //  $('div.CodeMirror-gutter div.CodeMirror-linenumber', wrapper).show();
    // });
    // cm.on("blur", function(cm, e) {
    //  $('div.CodeMirror-gutter div.CodeMirror-linenumber', wrapper).hide();
    // });
    cm.on("change", function(e) {
        try {
            clearTimeout(cm.writeback_timeout);
        } catch (err) {}

        cm.writeback_timeout = setTimeout(() => {
            let val = cm.getValue();
            // if it's the same as the placeholder, nullify
            if (placeholder == val) {
                val = "";
            }

            // write to the original textarea
            $(el)
                .val(val)
                .trigger('input');
        }, 400);
    });
}

/* Create a json editor textbox (using codemirror) */
utility.json_editor = function (el) {
    let placeholder = $(el).attr('placeholder');
    if (placeholder && !$(el).val()) {
        $(el).val(placeholder);
    }
    let cm = CodeMirror.fromTextArea(el, {
        mode: "javascript",
        json: true,
        indentUnit: 4,
        matchBrackets: true,
        autoCloseBrackets: true,
        inputStyle: "contenteditable",
        extraKeys: {
            Tab: function(cm) {
                if (!cm.getSelection().length) {
                    cm.replaceSelection(" ".repeat(cm.getOption("indentUnit")));
                } else {
                    return CodeMirror.Pass;
                }
            },
        }
    });
    let wrapper = $(cm.getWrapperElement());
    cm.on("change", function(e) {
        try {
            clearTimeout(cm.writeback_timeout);
        } catch (err) {}

        cm.writeback_timeout = setTimeout(() => {
            let val = cm.getValue();

            // check syntax
            try {
                if (val.length) {
                    JSON.parse(val);
                }
                wrapper.removeClass('cm-parseerror');
            } catch {
                wrapper.addClass('cm-parseerror');
            }

            // if it's the same as the placeholder, nullify
            if (placeholder == val) {
                val = "";
            }

            // write to the original textarea
            $(el)
                .val(val)
                .trigger('input');
        }, 400);
    });
}

/* determine whether an element is empty */
utility.notEmpty = function(val) {
    return (val && Object.keys(val).length > 0);
}

/* determine whether an element is an object */
utility.isObject = function (val) {
    return (val.constructor === Object);
}

/* determine whether an object is empty */
utility.isObjectEmpty = function (val) {
    return (Object.keys(val).length == 0);
}

/* check if the element is null or undefined */
utility.isNull = function (val) {
    return (val === null || val == undefined);
}

utility.blockUI = function (msg) {
    if (msg !== undefined) {
        msg = '<h1>'+msg+'<h1>';
    }

    $.blockUI({
        message: msg,
        css: {
            border: 'none',
            padding: '10px',
            backgroundColor: '#000',
            '-webkit-border-radius': '10px',
            '-moz-border-radius': '10px',
            opacity: .5,
            color: '#fff',
            cursor: 'default'
        },
        overlayCSS: {
            cursor: 'default'
        },
        fadeIn: 0,
        fadeOut: 0
    });
}

utility.unblockUI = function () {
    $.unblockUI();
}

utility.blockEl = function (element, msg) {
    if (msg == undefined)
        msg = null

    element.block({
        message: msg,
        css: {
            border: 'none',
            padding: '15px',
            backgroundColor: '#fff',
            '-webkit-border-radius': '10px',
            '-moz-border-radius': '10px',
            opacity: 1,
            color: '#fff',
            cursor: 'default'
        },
        fadeIn: 0,
        fadeOut: 0
    });
}

utility.unblockEl = function (element) {
    element.unblock();
}

function remove_whitespace(str) {
    return str.replace(/ /g,'');
}

function get_regex (str) {
    var re;
    try {
        re = new RegExp(str, 'i');
    } catch (err) {
        re = new RegExp("\\" + str, 'i');
    }
    return re
}

utility.findAll = function(regex, string) {
    re = new RegExp(str, 'ig');
}

utility.escape = function (unsafe) {
    try {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    } catch {
        return unsafe;
    }
}

utility.selector_enc = function (str) {
    return str
        .replace(/([#;?%&,.+*~\':"!^$[\]()=>|\/@])/g,'\\$1');
}

utility.deep_copy = function (d) {
    return JSON.parse(JSON.stringify(d));
}

utility.name_enc = function (str) {
    return encodeURIComponent(
        str.replace(/\//g,'__'));
}

emoticon_map = {
    ':)': '&#128578;',
    ':-)': '&#128578;',
    ':D': '&#128512;',
    ':-D': '&#128512;;',
    ':/': '&#128533;',
    ':-/': '&#128533;',
    ';)': '&#128521;',
    ';-)': '&#128521;',
    ':p': '&#128523;',
    ':-p': '&#128523;',
    ':(': '&#128577;',
    ':-(': '&#128577;',
    ";p": "&#128540;",
    ";-p": "&#128540;",
    ":'(": "&#128546;",
    "<3": "\u2764\uFE0F",
    "</3": "\uD83D\uDC94",
};

function escapeSpecialChars(regex) {
   return regex.replace(/([()[{*+.$^\\|?])/g, '\\$1');
 }

utility.emoticon_replace = function(text) {
    for (var i in emoticon_map) {
        var regex = new RegExp(escapeSpecialChars(i), 'gim');
        text = text.replace(regex, emoticon_map[i]);
    }
    return text;
};
utility.emoticon_replace = function (text) {
    for (var key in emoticon_map) {
        text = text.replace(key, emoticon_map[key]);
    }
    return text;
}

function yaml_enc (str) {
    /* condition the text */
    // space after colon
    str = str.replace(/(\n[^:]*):([^\s])/g, '$1: $2');
    // space after '-' for list
    str = str.replace(/(\n\s*)-([^\s])/g, '$1- $2');

    return str;
}

utility.api_url = function (url, path = []) {
    return [api_root, url].concat(path).join('/') + '/';
}

utility.static_url = function (str) {
    return static_root + str;
}

utility.ws_url = function(url) {
    var ws_proto = window.location.protocol == "https:" ? "wss" : "ws";
    return ws_proto + '://' + window.location.host + [root, 'ws', url].join('/') + '/';
}

utility.download_json_as_file = function(data, filename) {
    // format the data
    var blob = new Blob([JSON.stringify(data)], {type: "application/json"});

    // Create an invisible A element
    const a = document.createElement("a")
    a.style.display = "none";
    a.download = filename;
    a.href = window.URL.createObjectURL(blob);

    // add to the page
    document.body.appendChild(a);

    // Trigger the download by simulating click
    a.click();

    // Cleanup
    window.URL.revokeObjectURL(a.href);
    document.body.removeChild(a);
}

utility.range = function(start, end) {
    var size = end - start;
    return [...Array(size).keys()].map(i => i + start);
}

utility.merge = function (a, b) {
    if (Array.isArray(a)) {
        return a.concat(b);
    } else {
        return {...a, ...b};
    }
}

utility.tree_path = function (tree) {
    let path_d = {}
    utility.tree_path_helper(path_d, tree);
    return path_d;
}

utility.tree_path_helper = function (path_d, pointer, path) {
    path = path || [];

    for (var key in pointer) {
        path_d[key] = [...path];
        path.push(key);
        utility.tree_path_helper(path_d, pointer[key], path);
    }
}

utility.strip_html = function(html) {
    let el = $.parseHTML(html);

    // filter the nodes
    var filter = ['Text', 'HTMLTitleElement', 'HTMLStyleElement', 'Comment',
                  'HTMLMetaElement', 'HTMLLinkElement', 'HTMLImageElement'];
    var filtered_node_l = [];
    for (var i = 0; i < el.length; i++) {
        var node = el[i];
        if (filter.indexOf(node.constructor.name) < 0) {
            filtered_node_l.push(node);
        }
    }
    return filtered_node_l;
}

utility.basename = function (path) {
    return path.split('/').reverse()[0];
}

/*
 * Prototypes for built in types
 */
String.prototype.startsWith = function (str)
{
    return this.indexOf(str) == 0;
}

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}
String.prototype.lower = function() {
    return this.toLowerCase();
}

Array.prototype.last = function(val) {
    if (val) {
        this[this.length-1] = val;
    } else {
        return this[this.length-1];
    }
}

Array.prototype.remove = function(val) {
    var index = this.indexOf(val);
    if (index > -1) {
        this.splice(index, 1);
    }
    return this;
}

Array.prototype.contains = function(val) {
    return (this.indexOf(val) >= 0);
}

Array.prototype.sortIndexOf = function(val) {
    var index = this.indexOf(val);
    if (index < 0) {
        index = this.length;
    }
    return index;
}

Array.prototype.sortByKey = function(key) {
    return this.sort(function(a, b) {
        var x = b[key]; var y = a[key];
        return ((x <= y) ? 1 : -1);
    });
}

Array.prototype.shuffle = function() {
    var currentIndex = this.length,  randomIndex;

    // While there remain elements to shuffle...
    while (currentIndex != 0) {

        // Pick a remaining element...
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;

        // And swap it with the current element.
        [this[currentIndex], this[randomIndex]] = [
            this[randomIndex], this[currentIndex]];
    }

    return this;
}
Array.prototype.isEmpty = function() {
    return this.length === 0;
}

Array.prototype.toDict = function(key) {
    var dict = {};
    for (var i = 0; i < this.length; i++) {
        let el = this[i];
        dict[el[key]] = el;
    }
    return dict;
}

utility.getTimeFromEpoch = function (epoch) {
    return moment(epoch * 1000);
}
utility.getDateString = function (date) {
    if (typeof date == "number") date = utility.getTimeFromEpoch(date);

    var ret = "";
    var now = moment();

    // is the day the same?
    if (now.diff(date, 'months', true) > 10) {
        ret = date.format('MM/DD/YYYY');
    } else if (now.diff(date, "days") > 6) {
        ret = date.format('MMM DD');
    } else {
        ret = date.format('ddd');
    }

    return ret;
}
utility.getTimeString = function (date, mil_time, seconds) {
    if (typeof date == "number") date = utility.getTimeFromEpoch(date);
    if (mil_time === undefined) mil_time = false;
    if (seconds === undefined) seconds = false;

    var ret = "";
    var now = moment();

    // is the day the same?
    if (now.diff(date, 'months', true) > 10) {
        ret += date.format('MM/DD/YYYY ');
    } else if (now.diff(date, "days") > 1) {
        if (now.diff(date, "days") > 6) {
            ret += date.format('MMM DD ');
        } else {
            ret += date.format('ddd ');
        }
    }

    if (mil_time) {
        if (seconds)
            ret += date.format('HH:mm:ss');
        else
            ret += date.format('HH:mm');
    } else {
        if (seconds)
            ret += date.format('h:mm:ss A');
        else
            ret += date.format('h:mm A');
    }
    return ret
}

utility.notify = function (title, body, icon, link) {
    if (Notification.permission !== 'granted')
        Notification.requestPermission();
    else {
        var notification = new Notification(title, {
            icon: icon,
            body: body,
        });
        notification.onclick = function() {
            document.location.hash = link;
        };
    }
}

utility.placeCursorAtEnd = function (el) {
    el.focus();
    if (typeof window.getSelection != "undefined"
        && typeof document.createRange != "undefined") {
        var range = document.createRange();
        range.selectNodeContents(el);
        range.collapse(false);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
    } else if (typeof document.body.createTextRange != "undefined") {
        var textRange = document.body.createTextRange();
        textRange.moveToElementText(el);
        textRange.collapse(false);
        textRange.select();
    }
}

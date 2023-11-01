class Element {
    add_to_page () {
        // add to the page
        if (this.container) {
            if (append) {
                this.container.append(this.html);
            } else {
                this.container.html(this.html);
            }
            this.el = this.container.children().last();
        }
    }
}

class Input extends Element {
    constructor (container, config = {}, append = true) {
        super();

        this.container = container;
        this.el = null;
        this.html = "";

        // read config
        this.label = config.label || "";
        this.id = config.id || this.label.lower().replace(/ /g,"_");
        this.hidden = config.hidden;
        this.width = config.width || "50%";
        this.required = config.required || false;
        this.value = config.value || "";

        this.init();

        /* save value */
        this.el.on("input", function (e) {
            this.value = this.el.find('input').val();
        })
    }

    init () {
        this.html = `<label class="form" style="width: calc(${this.width} - 28px)"`+
            `hidden=${this.hidden}>${this.label}${(this.required ? "*":"")}`+
            `<br><input name="${this.id}" value="${this.value}"/></label>`;

        this.add_to_page();
    }
}

function thread_object (thread_cfg) {
    var self = utility.merge(this, thread_cfg);

    // convert user id to user object
    if (self.user) {
        self.user = fp.user_d[self.user];
    }

    /*
     * initialize/build the picture html code (either profile picture or chat icon)
     */
    if (!self.user) {
        // Get the initials
        let words = self.label.split(" ")
        let initials = "";
        for (var word of words) {
            initials += word[0].capitalize();
        }
        initials = initials.slice(0,2);

        // get the color
        let color = Math.floor(Math.random()*16777215).toString(16);

        // set the html
        self.pic_svg = `<svg class="pic">
                         <circle cx="20" cy="20" r="20" fill="#${color}"/>
                         <text x="50%" y="54%" fill="white">${initials}</text>
                       </svg>`;
    }

    /*
     * Check whether the chat thread is currently being viewed
     */
    self.in_view = function () {
        return Boolean(fp.content &&
                       fp.content.constructor.name == "chat_thread" &&
                       fp.content.id == self.id);
    }

    return self;
}

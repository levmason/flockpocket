function profile_pic_uploader (container, config, append = true) {
    var self = this;
    form_el.call(self, container, config, append);

    // init config
    if (self.value) {
        self.avatar = utility.static_url('profile_pics/'+self.value);
    } else {
        self.avatar = utility.static_url('profile_pics/avatar.svg');
    }

    // initialize the element
    self.init = function () {
        self.html += '<div class="prof_pic_uploader">'+
            '<img id="profile_pic" src="'+self.avatar+'"/>';
        self.html += '<label class="button">'+
            '<input id="upload_pic" type="file" accept="image/png, image/jpeg">'+
            'Upload Profile Image</label>';
        self.html += '</div>';

        self.add_to_page();
        self.init_handlers();
    }

    // initialize handlers
    self.init_handlers = function () {
        // clear the input when opening
        self.el.on("click", "input#upload_pic", function(e) {
            $(this).val('');
        })

        // Handle input
        self.el.on("input", "input#upload_pic", function(e) {
            // get the file object
            let file = e.target.files[0];
            if (file) {

                // create a file reader
                const reader = new FileReader();
                reader.addEventListener('load', (event) => {
                    // get the file url
                    let url = event.target.result;

                    // open the popup
                    modal.open('<div id="cropper"></div><div width="100%">'+
                               '<button id="cropper_done">Done</button></div>');

                    // fill with croppie
                    var el = document.getElementById('cropper');
                    var cropper = new Croppie (el, {
                        viewport: { width: 300, height: 300, type: 'circle' },
                        url: url
                    })

                    // on done
                    $('button#cropper_done').on("click", function(e) {
                        cropper.result('blob', 'viewport', 'jpeg').then(function(blob) {
                            // remember the data
                            self.value = blob;
                            // update the UI
                            var blobUrl = URL.createObjectURL(blob);
                            $('img#profile_pic').attr("src",blobUrl);
                            // close the modal
                            modal.close();
                        });
                    })
                });
                reader.readAsDataURL(file);
            }
        })
    }
}

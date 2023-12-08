function user (config) {
    var self = utility.merge(this, config);

    // initialize attributes
    self.pic_url = utility.static_url('profile_pics/'+ (self.pic || "avatar.svg"));

    self.possible_relationships = function () {
        let taken = new Set();
        for (let rel of self.family) {
            let type_details = cfg.relationship_types[rel.type];
            if (type_details.unique) {
                taken.add(rel.type);
            }
        }

        let rel_l = [];
        for (var type_label in cfg.relationship_types) {
            let type_details = cfg.relationship_types[type_label];

            // make sure we're the right gender
            if (type_details.required_gender && self.gender != type_details.required_gender) {
                continue;
            }

            // make sure this isn't a unique relationship that's already set
            if (type_details.unique && taken.has(type_label)) {
                continue;
            }

            rel_l.push(type_label);
        }
        return rel_l;
    }

    return self;
}

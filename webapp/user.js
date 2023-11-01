function user (user) {
    var self = utility.merge(this, user);
    self.full_name = `${self.first_name} ${self.last_name}`;
}

cfg = {
    relationship_types: {
        'Husband': {
            gender: "Male",
            required_gender: "Female",
            unique: true,
        },
        'Wife': {
            gender: "Female",
            required_gender: "Male",
            unique: true,
        },
        'Son': {
            gender: "Male",
        },
        'Daughter': {
            gender: "Female",
        },
        'Brother': {
            gender: "Male",
        },
        'Sister': {
            gender: "Female",
        },
        'Father': {
            gender: "Male",
            unique: true,
        },
        'Mother': {
            gender: "Female",
            unique: true,
        },
        'Grandfather': {
            gender: "Male",
        },
        'Grandmother': {
            gender: "Female",
        },
        'Grandson': {
            gender: "Male",
        },
        'Granddaughter': {
            gender: "Female",
        },
    }
}

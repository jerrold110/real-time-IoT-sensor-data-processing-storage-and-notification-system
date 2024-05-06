db.createUser(
    {
        user: "abc",
        pwd: "abc",
        roles: [
            {
                role: "readWrite",
                db: "a_db"
            }
        ]
    }
);
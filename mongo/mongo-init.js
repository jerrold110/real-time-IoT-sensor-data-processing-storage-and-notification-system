// this creates the new user in the database sensors instead of test when i use db
var adminDB = db.getSiblingDB('admin');
adminDB.auth('root', 'root');

adminDB = adminDB.getSiblingDB('sensors');
adminDB.createUser({
  user: 'sensor_user',
  pwd: 'sensor_pass',
  roles: 
    [{
        role: "readWrite",
        db: "sensors"
    }],
});

adminDB.createCollection('temperature');
adminDB.createCollection('humidity');

// mongosh -u root -p root
// mongosh -u sensor_user -p sensor_pass --authenticationDatabase sensors

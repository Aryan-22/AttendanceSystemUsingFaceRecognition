import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{

    "databaseURL":"https://faceattendancerealtime-7f1f9-default-rtdb.firebaseio.com/"
})
ref = db.reference("Students")
data = {

"1":
    {
        "name": "Emily Blunt",
         "Branch":"Information Technology",
         "starting_year":2023,
         "total_attendance":20,
          "year":3,
          "last_attendance":"2024-02-11 11:02:59"


    },
"2":
    {
        "name": "Elon Musk",
         "Branch":"Physics",
         "starting_year":2022,
         "total_attendance":20,
          "year":2,
          "last_attendance":"2024-05-02 10:03:59"


    }
}
for key,val in data.items():
    ref.child(key).set(val)
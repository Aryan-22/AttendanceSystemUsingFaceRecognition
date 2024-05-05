import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{

    "databaseURL":"https://faceattendancerealtime-7f1f9-default-rtdb.firebaseio.com/",
    "storageBucket":"faceattendancerealtime-7f1f9.appspot.com"
})
#importing the student images into a list
folderpath = "images"
pathlist = os.listdir(folderpath)
print(pathlist)
imglist = []
studentids = []
for path in pathlist:
    imglist.append(cv2.imread(os.path.join(folderpath,path)))
    studentids.append(os.path.splitext(path)[0])
    filename = f'{folderpath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
print(studentids)
def findencodings(imageslist):
    encodelist = []

    for img in imageslist:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodelist.append(encode)
    return encodelist
print("encoding started")
encodelistkown = findencodings(imglist)
encodinglistknownwithids = [encodelistkown,studentids]
print("encoding complete!")
file = open('Encodefile.p','wb')
pickle.dump(encodinglistknownwithids,file)
file.close()
print("file saved")


import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import datetime
from datetime import datetime
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{

    "databaseURL":"https://faceattendancerealtime-7f1f9-default-rtdb.firebaseio.com/",
    "storageBucket":"faceattendancerealtime-7f1f9.appspot.com"
})

bucket = storage.bucket()
cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)
img_background = cv2.imread("Resources/background.png")
#importing the mode images into a list
foldermodepath = "Resources/Modes"
modepath = os.listdir(foldermodepath)
imgmodelist = []
for path in modepath:
    imgmodelist.append(cv2.imread(os.path.join(foldermodepath,path)))
#print(len(imgmodelist))
#load the encoding file
print('loading encode file..')
file = open('Encodefile.p','rb')
encodelistknownwithids = pickle.load(file)
encodelistkown,studentids = encodelistknownwithids
file.close()
#print(studentids)
print('encode file loaded!')
modetype = 0
counter = 0
id = -1
imgstudent = []
while True:
    success,img = cap.read()
    imgs = cv2.resize(img,(0,0),None,0.25,0.25)
    imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)
    face_current_frame = face_recognition.face_locations(imgs)
    encode_current_frame = face_recognition.face_encodings(imgs,face_current_frame)
    img_background[162:162 + 480,55:55 + 640] = img
    img_background[44:44 + 633, 808:808 + 414] = imgmodelist[modetype]
    if face_current_frame:

        for encodeface,facelocation in zip(encode_current_frame,face_current_frame):
            matches = face_recognition.compare_faces(encodelistkown,encodeface)
            face_distance = face_recognition.face_distance(encodelistkown,encodeface)
            #print(matches)
            #print(face_distance)
            #print(matches,face_distance)
            match_index = np.argmin(face_distance)
            #print(match_index)
            if matches[match_index]:
                #print('known face detected')
                #print(studentids[match_index])
                y1,x2,y2,x1 = facelocation
                y1,x2,y2,x1 = y1 * 4,x2 * 4,y2 * 4,x1 * 4
                bbox = 55 + x1,162 + y1, x2 - x1,y2 - y1 #starting points and width,height
                img_background = cvzone.cornerRect(img_background,bbox,rt = 0)
                id = studentids[match_index]
                if counter == 0:
                    counter = 1
                    modetype = 1
        if counter != 0:
            if counter == 1:
                #get data from firebase
                studentinfo = db.reference(f"Students/{id}").get()
                print(studentinfo)
                #get image from storage
                blob = bucket.get_blob(f'images/{id}.png')
                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgstudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                #update data of attendance
                datetimeobject = datetime.strptime(studentinfo['last_attendance'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondselapsed = (datetime.now() - datetimeobject).total_seconds()
                if secondselapsed >= 24 * 60 * 60:

                    ref = db.reference(f"Students/{id}")
                    studentinfo["total_attendance"] += 1
                    ref.child('total_attendance').set(studentinfo["total_attendance"])
                    ref.child("last_attendance").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modetype = 3
                img_background[44:44 + 633, 808:808 + 414] = imgmodelist[modetype]
            if modetype != 3:

                if 10 < counter < 20:
                    modetype = 2
                img_background[44:44 + 633, 808:808 + 414] = imgmodelist[modetype]

                if counter <= 10:

                    cv2.putText(img_background,str(studentinfo['total_attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)

                    cv2.putText(img_background, str(studentinfo['Branch']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (255, 255, 255), 1)
                    cv2.putText(img_background, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (255, 255, 255), 1)
                    cv2.putText(img_background, str(studentinfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)
                    cv2.putText(img_background, str(studentinfo['starting_year']), (1125, 125), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)
                    (w,h),_= cv2.getTextSize(studentinfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414 - w) // 2
                    cv2.putText(img_background, str(studentinfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (50, 50, 50), 1)
                    img_background[175:175+216,909:909+216] = imgstudent
        counter += 1
        if counter >= 20:
            counter = 0
            modetype = 0
            studentinfo = []
            imgstudent = []
            img_background[44:44 + 633, 808:808 + 414] = imgmodelist[modetype]

        else:
            counter = 0
            mode = 0
        #cv2.imshow("Webcam",img)
    cv2.imshow("Face attendance",img_background)
    cv2.waitKey(1)

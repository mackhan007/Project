import os
import cv2
import json
import pickle
import numpy as np
from time import time
from shutil import copy2
import face_recognition

class FaceRecognizer:
    def __init__(self) -> None:
        self.projectDir = os.getcwd()
        
        self.cwd = f'{self.projectDir}/faceRec'
        self.sampleFile = f'{self.projectDir}/data/sample'
        cascPath=os.path.dirname(cv2.__file__)+"/data/haarcascade_frontalface_default.xml"
        self.faceDetector = cv2.CascadeClassifier(cascPath)

        self.isVideoOn = False
        self.video = None

        self.lastUser = None
        self.faceName = None
        
        self.onUserChangeCallback = None

        # self.faces = 0
        # self.currentFaceDetected = None

        self.known_face_encodings = []  
        self.known_face_names = []  
        self.reference_data = {}
        self.face_data = {}

        print('FR INIT')

    def initVideo(self):
        self.isVideoOn = True
        self.video = cv2.VideoCapture(0)

    # def startIsFacePresent(self):
    #     if not self.isVideoOn or not self.video: self.initVideo()

    #     while self.isVideoOn and self.video:
    #         ret, frames = self.video.read()

    #         gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY)

    #         faces = self.faceDetector.detectMultiScale(
    #             gray,
    #             scaleFactor=1.1,
    #             minNeighbors=5,
    #             minSize=(30, 30),
    #             flags=cv2.CASCADE_SCALE_IMAGE
    #         )

    #         self.faces = faces
    #         print(self.faces)
    
    # def isFacePresent(self):
    #     return len(self.faces) > 0

    # def hasMultipleFaces(self):
    #     return len(self.faces) > 1



    def loadDataFromFile(self):
        self.known_face_encodings = []  
        self.known_face_names = []  
        self.reference_data = {}
        self.face_data = {}

        try:
            file = open(os.path.join(self.cwd, "data/reference_data.pkl"), "rb")
            self.reference_data = pickle.load(file)        
            file.close()

            file = open(os.path.join(self.cwd, "data/face_data.pkl"), "rb")
            self.face_data = pickle.load(file)      
            file.close()

            for ref_id , embed_list in self.face_data.items():
                for my_embed in embed_list:
                    self.known_face_encodings += [my_embed]
                    self.known_face_names += [ref_id]        

        except: 
            print('unable to load data')
            pass

    def createData(self, name, id):
        dir = 'data/'

        if not os.path.exists(os.path.join(self.cwd, dir)):
            os.makedirs(os.path.join(self.cwd, dir))

        try:
            referenceFile = open(os.path.join(self.cwd, "data/reference_data.pkl"), "rb")
            faceDataFile = open(os.path.join(self.cwd, "data/face_data.pkl"), "rb")

            self.reference_data = pickle.load(referenceFile)
            self.face_data = pickle.load(faceDataFile)

            referenceFile.close()
            faceDataFile.close()
        except:
            self.reference_data = {}
            self.face_data = {}

        self.reference_data[id] = name

        try:
            referenceFile = open(os.path.join(self.cwd, "data/reference_data.pkl"), "wb")
            pickle.dump(self.reference_data, referenceFile)
            referenceFile.close() 
        except:
            pass
    
    def dumpTrainingData(self):
        faceDataFile = open(os.path.join(self.cwd, "data/face_data.pkl"), "wb")
        pickle.dump(self.face_data,faceDataFile)
        faceDataFile.close()
        
    def createUsersDataset(self, name):
        file_location = f'{self.projectDir}/data/{name}'
        task_location = f'{file_location}/tasks'
        if not os.path.exists(file_location):
            os.makedirs(file_location)  

        if not os.path.exists(task_location):
            os.makedirs(task_location)   

        copy2(self.sampleFile + '/command.json', file_location + '/command.json')
        copy2(self.sampleFile + '/reply.json', file_location + '/reply.json')
        
        copy2(self.sampleFile + '/tell_me_time_reply.txt', task_location + '/tell_me_time_reply.txt')
        copy2(self.sampleFile + '/tell_me_time_steps.json', task_location + '/tell_me_time_steps.json')
               

    def captureAndTrain(self, name, id):
        if not self.isVideoOn or not self.video: self.initVideo()
        self.createData(name, id)

        for _ in range(10):
            while True:
                try:
                    check, frame = self.video.read()

                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small_frame = small_frame[:, :, ::-1]

                    try:
                        face_locations = face_recognition.face_locations(rgb_small_frame)
                        if face_locations != []:
                            print(face_locations)
                            face_encoding = face_recognition.face_encodings(frame)[0]
                            if id in self.face_data:
                                self.face_data[id]+=[face_encoding]
                            else:
                                self.face_data[id]=[face_encoding]    
                            break
                    except: 
                        pass
                    
                except:
                    pass

        self.createUsersDataset(name)
        self.dumpTrainingData()
        self.loadDataFromFile()

    def onUserChange(self):
        try:
            if self.faceName != self.lastUser:
                self.onUserChangeCallback(self.faceName)
        except:
            pass
    
    def registerForOnUserChange(self, callback):
        self.onUserChangeCallback = callback
        

    def startRecognizingFace(self):
        print('FR RUN FACEREC')
        if not self.isVideoOn or not self.video: self.initVideo()
        self.loadDataFromFile()

        while self.isVideoOn and self.video: 
            face_locations = []
            face_encodings = []
            face_names = []
            process_this_frame = True

            ret, frame = self.video.read()
            try:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]

                if process_this_frame:

                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    face_names = []
                    for face_encoding in face_encodings:

                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        name = "Unknown"

                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        try:
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = self.known_face_names[best_match_index]
                        except:
                            pass

                        face_names.append(name)
                
                if len(face_names) >= 1:
                    self.faceName = ("Unknown" if face_names[0] == "Unknown" else self.reference_data[face_names[0]]).lower()
                    self.onUserChange()
                    self.lastUser = self.faceName.lower()
                else:
                    self.faceName = None
                    
                
                # print(self.faceName)

                process_this_frame = not process_this_frame

                for (top_s, right, bottom, left), name in zip(face_locations, face_names):
                    top_s *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    cv2.rectangle(frame, (left, top_s), (right, bottom), (0, 0, 255), 2)

                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, 'Unknown' if name == 'Unknown' else self.reference_data[name], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                font = cv2.FONT_HERSHEY_DUPLEX
                
            except:
                pass


            '''
                uncomment for unit testing
            '''
            # cv2.imshow('Video', frame)

            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

    def stopRecognition(self):
        print('STOP FACE REC')
        self.isVideoOn = False
        self.video.release()
        self.video = None


# fr = FaceRecognizer()

# fr.captureAndTrain('Aman Khan', time())

# fr.startRecognizingFace()



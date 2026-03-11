# face_utils.py
import cv2, os, numpy as np

CASCADE_FACE = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
CASCADE_EYE  = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_eye.xml")

FACE_DIR="static/faces"
SIZE=(200,200)
THRESHOLD=70

def preprocess(path):
    img=cv2.imread(path)
    if img is None: return None
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces=CASCADE_FACE.detectMultiScale(gray,1.3,5)
    if len(faces)==0: return None
    x,y,w,h=faces[0]
    face=gray[y:y+h,x:x+w]
    return cv2.resize(face,SIZE)

def train():
    faces=[]
    labels=[]
    label_map={}
    i=0
    for user in os.listdir(FACE_DIR):
        label_map[i]=user
        for img in os.listdir(FACE_DIR+"/"+user):
            f=preprocess(FACE_DIR+"/"+user+"/"+img)
            if f is not None:
                faces.append(f)
                labels.append(i)
        i+=1
    model=cv2.face.LBPHFaceRecognizer_create()
    model.train(faces,np.array(labels))
    return model,label_map

def spoof_check(path):
    img=cv2.imread(path)
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    eyes=CASCADE_EYE.detectMultiScale(gray)
    return len(eyes)>=1

def liveness_check(img1,img2):
    a=cv2.imread(img1,0)
    b=cv2.imread(img2,0)
    diff=cv2.absdiff(a,b)
    return diff.mean()>3

def verify_face(username,img1,img2):
    if not spoof_check(img1): return False
    if not liveness_check(img1,img2): return False

    model,map=train()
    face=preprocess(img1)
    label,conf=model.predict(face)
    return map[label]==username and conf<THRESHOLD
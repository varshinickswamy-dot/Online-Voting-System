import cv2,time

def record_video(path,seconds=5):
    cam=cv2.VideoCapture(0)
    fourcc=cv2.VideoWriter_fourcc(*'XVID')
    out=cv2.VideoWriter(path,fourcc,20.0,(640,480))
    start=time.time()

    while time.time()-start<seconds:
        ret,frame=cam.read()
        if ret:
            out.write(frame)
    cam.release()
    out.release()
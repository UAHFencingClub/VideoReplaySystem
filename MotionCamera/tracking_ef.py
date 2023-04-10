import cv2
import sys
import numpy as np
 
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
 
if __name__ == '__main__' : 
    # Read video
    #video = cv2.VideoCapture("input.mp4")
    video = cv2.VideoCapture(0) # for using CAM
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)
 
    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video")
        sys.exit()
 
    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print ('Cannot read video file')
        sys.exit()
     
    qcd = cv2.QRCodeDetector()

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break
         
        img = frame

        retval, decoded_info, points, straight_qrcode = qcd.detectAndDecodeMulti(frame)
        if retval:
            img = cv2.polylines(img, points.astype(int), True, (0, 255, 0), 3)
        cv2.imshow('keypoints',img)
 
        # Exit if ESC pressed
        if cv2.waitKey(1) & 0xFF == ord('q'): # if press SPACE bar
            break
    video.release()
    cv2.destroyAllWindows()
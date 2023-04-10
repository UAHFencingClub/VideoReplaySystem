#From https://gist.githubusercontent.com/aarmea/629e59ac7b640a60340145809b1c9013/raw/ad31081e10c48f5d7beeae762948683158f966b5/1-capture.py
#modified for our use
import numpy as np
import cv2
import time

LEFT_PATH = "L{:06d}.jpg"
RIGHT_PATH = "R{:06d}.jpg"

#2560X960@ 60fps/2560X720@60fps /1280X480@60fps /640X240@60fps 
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 480

# TODO: Use more stable identifiers
stereo_camera = cv2.VideoCapture(2)
stereo_camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
stereo_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

# The distortion in the left and right edges prevents a good calibration, so
# discard the edges
CROP_WIDTH = 960
def cropHorizontal(image):
    return image[:,
            int((CAMERA_WIDTH-CROP_WIDTH)/2):
            int(CROP_WIDTH+(CAMERA_WIDTH-CROP_WIDTH)/2)]

frameId = 0

# Grab both frames first, then retrieve to minimize latency between cameras
while(True):
    ret, frame = stereo_camera.read()
    (imageHeight, imageWidth) = frame.shape[:2]
    centerFrame = imageWidth//2
    leftFrame = frame[0:imageHeight, 0:centerFrame]
    rightFrame = frame[0:imageHeight, centerFrame:imageWidth]
    
    #leftFrame = cropHorizontal(leftFrame)
    #rightFrame = cropHorizontal(rightFrame)

    cv2.imshow('left', leftFrame)
    cv2.imshow('right', rightFrame)

    cv2.imwrite(LEFT_PATH.format(frameId), leftFrame)
    cv2.imwrite(RIGHT_PATH.format(frameId), rightFrame)
    
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    #elif key & 0xFF == ord('s'):
    #    print("cap")
    #    cv2.imwrite(LEFT_PATH.format(frameId), leftFrame)
    #    cv2.imwrite(RIGHT_PATH.format(frameId), rightFrame)
        

    frameId += 1
    time.sleep(0.5)

stereo_camera.release()
cv2.destroyAllWindows()

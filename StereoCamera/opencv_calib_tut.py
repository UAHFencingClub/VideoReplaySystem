# Found at https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_calib3d/py_calibration/py_calibration.html#calibration

import numpy as np
import cv2
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('*.jpg')

CAMERA_WIDTH=1280
CAMERA_HEIGHT=480

LEFT_PATH = "L{:06d}.jpg"
RIGHT_PATH = "R{:06d}.jpg"

CHESS_SIZE=(6,4)

stereo_camera = cv2.VideoCapture(1)

stereo_camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
stereo_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

frameId = 0

while True:
    ret, frame = stereo_camera.read()
    (imageHeight, imageWidth) = frame.shape[:2]
    centerFrame = imageWidth//2
    leftImage = frame[0:imageHeight, 0:centerFrame]
    rightImage = frame[0:imageHeight, centerFrame:imageWidth]

    grayRight = cv2.cvtColor(rightImage, cv2.COLOR_BGR2GRAY)
    grayLeft = cv2.cvtColor(leftImage, cv2.COLOR_RGB2GRAY)

    # Find the chess board corners
    retR, cornersRight = cv2.findChessboardCorners(grayRight, CHESS_SIZE,None)
    retL, cornersLeft = cv2.findChessboardCorners(grayLeft, CHESS_SIZE,None)
    # If found, add object points, image points (after refining them)
    if retR & retL:
        cv2.imwrite(LEFT_PATH.format(frameId), leftImage)
        cv2.imwrite(RIGHT_PATH.format(frameId), rightImage)
        frameId += 1

    if retR == True:
        objpoints.append(objp)

        cv2.cornerSubPix(grayRight,cornersRight,(11,11),(-1,-1),criteria)
        imgpoints.append(cornersRight)

        # Draw and display the corners
        cv2.drawChessboardCorners(rightImage, CHESS_SIZE, cornersRight,ret)
        cv2.imshow('imgR',rightImage)
        
        cv2.waitKey(100)
    else:
        cv2.imshow('imgR',rightImage)
        cv2.waitKey(100)

    if retL == True:        
        objpoints.append(objp)

        cv2.cornerSubPix(grayLeft,cornersLeft,(11,11),(-1,-1),criteria)
        imgpoints.append(cornersLeft)

        # Draw and display the corners
        cv2.drawChessboardCorners(leftImage, CHESS_SIZE, cornersLeft,ret)
        cv2.imshow('imgL',leftImage)
        
        cv2.waitKey(100)
    else:
        cv2.imshow('imgL',leftImage)
        cv2.waitKey(100)
    #cv2.imshow('imgR',grayRight)

cv2.destroyAllWindows()
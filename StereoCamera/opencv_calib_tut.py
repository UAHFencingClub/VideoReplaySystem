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

stereo_camera = cv2.VideoCapture(2)

stereo_camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
stereo_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

while True:
    ret, frame = stereo_camera.read()
    (imageHeight, imageWidth) = frame.shape[:2]
    centerFrame = imageWidth//2
    leftImage = frame[0:imageHeight, 0:centerFrame]
    rightImage = frame[0:imageHeight, centerFrame:imageWidth]

    grayRight = cv2.cvtColor(rightImage, cv2.COLOR_BGR2GRAY)
    grayLeft = cv2.cvtColor(leftImage, cv2.COLOR_RGB2GRAY)

    # Find the chess board corners
    ret, cornersRight = cv2.findChessboardCorners(grayRight, (7,6),None)
    ret, cornersLeft = cv2.findChessboardCorners(grayLeft, (7,6),None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        cv2.cornerSubPix(grayRight,cornersRight,(11,11),(-1,-1),criteria)
        imgpoints.append(cornersRight)
        
        cv2.cornerSubPix(grayLeft,cornersLeft,(11,11),(-1,-1),criteria)
        imgpoints.append(cornersLeft)

        # Draw and display the corners
        cv2.drawChessboardCorners(leftImage, (7,6), cornersLeft,ret)
        cv2.drawChessboardCorners(rightImage, (7,6), cornersRight,ret)

        cv2.imshow('imgL_C',leftImage)
        cv2.imshow('imgR_C',rightImage)
        cv2.waitKey(500)

    cv2.imshow('imgL',grayLeft)
    cv2.imshow('imgR',grayRight)

cv2.destroyAllWindows()
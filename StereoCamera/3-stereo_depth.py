#From https://gist.githubusercontent.com/aarmea/629e59ac7b640a60340145809b1c9013/raw/ad31081e10c48f5d7beeae762948683158f966b5/3-stereo_depth.py
# Modified for our own uses. 

import sys
import numpy as np
import cv2

REMAP_INTERPOLATION = cv2.INTER_LINEAR

DEPTH_VISUALIZATION_SCALE = 2048

if len(sys.argv) != 2:
    print("Syntax: {0} CALIBRATION_FILE".format(sys.argv[0]))
    sys.exit(1)

calibration = np.load(sys.argv[1], allow_pickle=False)
imageSize = tuple(calibration["imageSize"])
leftMapX = calibration["leftMapX"]
leftMapY = calibration["leftMapY"]
leftROI = tuple(calibration["leftROI"])
rightMapX = calibration["rightMapX"]
rightMapY = calibration["rightMapY"]
rightROI = tuple(calibration["rightROI"])

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 480

# TODO: Use more stable identifiers
stereo_camera = cv2.VideoCapture(0)

stereo_camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
stereo_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

# The distortion in the left and right edges prevents a good calibration, so
# discard the edges
CROP_WIDTH = 1280
def cropHorizontal(image):
    return image[:,
            int((CAMERA_WIDTH-CROP_WIDTH)/2):
            int(CROP_WIDTH+(CAMERA_WIDTH-CROP_WIDTH)/2)]

# TODO: Why these values in particular?
# TODO: Try applying brightness/contrast/gamma adjustments to the images
stereoMatcher = cv2.StereoBM_create()
stereoMatcher.setMinDisparity(4)
stereoMatcher.setNumDisparities(128)
stereoMatcher.setBlockSize(21)
stereoMatcher.setROI1(leftROI)
stereoMatcher.setROI2(rightROI)
stereoMatcher.setSpeckleRange(16)
stereoMatcher.setSpeckleWindowSize(45)

# Grab both frames first, then retrieve to minimize latency between cameras
while(True):
    if not stereo_camera.grab():
        print("No more frames")
        break

    ret, frame = stereo_camera.read()
    (imageHeight, imageWidth) = frame.shape[:2]
    centerFrame = imageWidth//2
    leftFrame = frame[0:imageHeight, 0:centerFrame]
    rightFrame = frame[0:imageHeight, centerFrame:imageWidth]

    fixedLeft = cv2.remap(leftFrame, leftMapX, leftMapY, REMAP_INTERPOLATION)
    fixedRight = cv2.remap(rightFrame, rightMapX, rightMapY, REMAP_INTERPOLATION)

    grayLeft = cv2.cvtColor(fixedLeft, cv2.COLOR_BGR2GRAY)
    grayRight = cv2.cvtColor(fixedRight, cv2.COLOR_BGR2GRAY)
    depth = stereoMatcher.compute(grayLeft, grayRight)

    cv2.imshow('left', fixedLeft)
    cv2.imshow('right', fixedRight)
    cv2.imshow('depth', depth / DEPTH_VISUALIZATION_SCALE)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stereo_camera.release()
cv2.destroyAllWindows()

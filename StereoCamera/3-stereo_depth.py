#From https://gist.githubusercontent.com/aarmea/629e59ac7b640a60340145809b1c9013/raw/ad31081e10c48f5d7beeae762948683158f966b5/3-stereo_depth.py
# Modified for our own uses. 

import sys
import numpy as np
import cv2
#from matplotlib import pyplot as plot

REMAP_INTERPOLATION = cv2.INTER_LINEAR

DEPTH_VISUALIZATION_SCALE = 256

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
stereo_camera = cv2.VideoCapture(2)

stereo_camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
stereo_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

# TODO: Why these values in particular?
# TODO: Try applying brightness/contrast/gamma adjustments to the images
stereoMatcher = cv2.StereoBM_create()
stereoMatcher.setMinDisparity(-32)
stereoMatcher.setNumDisparities(4*16)
stereoMatcher.setBlockSize(21)
stereoMatcher.setROI1(leftROI)
stereoMatcher.setROI2(rightROI)
stereoMatcher.setSpeckleRange(16)
stereoMatcher.setTextureThreshold(100)
stereoMatcher.setSpeckleWindowSize(1500)


#Blob detection

#detector = cv2.SimpleBlobDetector()
# Setup SimpleBlobDetector parameters.
params = cv2.SimpleBlobDetector_Params()
 
params.filterByColor = True
params.blobColor = 255

# Change thresholds
params.minThreshold = 20;
params.maxThreshold = 220;
 
# Filter by Area.
params.filterByArea = True
params.minArea = 1500
 
# Filter by Circularity
params.filterByCircularity = False
params.minCircularity = 0.1
 
# Filter by Convexity
params.filterByConvexity = True
params.minConvexity = 0.87
 
# Filter by Inertia
params.filterByInertia = False
params.minInertiaRatio = 0.0001
params.maxInertiaRatio = 0.01
 
# Create a detector with the parameters
ver = (cv2.__version__).split('.')
if int(ver[0]) < 3 :
  detector = cv2.SimpleBlobDetector(params)
else : 
  detector = cv2.SimpleBlobDetector_create(params)

#end blob detection setup

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

    #Extra processing
    depth_norm = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    depth_equi = cv2.equalizeHist(depth_norm)
    depth_thresh = np.where(depth_equi < 100, 0, depth_equi)

    keypoints = detector.detect(depth_equi)
    im_with_keypoints = cv2.drawKeypoints(depth_equi, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    
    #cv2.imshow('depth_equi', depth_equi)
    cv2.imshow('depth_tresh', depth_thresh)
    cv2.imshow('keypoints',im_with_keypoints)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stereo_camera.release()
cv2.destroyAllWindows()

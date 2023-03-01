import cv2
import numpy
import glob


stereo_camera = cv2.VideoCapture(0)

def rescale_frame(frame, percent):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

#2560X960@ 60fps/2560X720@60fps /1280X480@60fps /640X240@60fps 
CAMERA_WIDTH=1280
CAMERA_HEIGHT=480


stereo_camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
stereo_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
stereo_compute = cv2.StereoBM_create(numDisparities=32, blockSize=15)

counter = 0

while True:
    #stereo_compute = cv2.StereoBM_create(numDisparities=16, blockSize=15)
    ret, frame = stereo_camera.read()
    resizeFrame = rescale_frame(frame, 50)
    (imageHeight, imageWidth) = resizeFrame.shape[:2]
    centerFrame = imageWidth//2
    leftImage = resizeFrame[0:imageHeight, 0:centerFrame]
    rightImage = resizeFrame[0:imageHeight, centerFrame:imageWidth]
    
    #lefth = leftImage.height()
    #leftw = leftImage.width()
    #righth = rightImage.height()
    #rightw = rightImage.width()
    
    cv2.imshow('leftIamge', leftImage)
    cv2.imshow('rightImage', rightImage)

    grayRight = cv2.cvtColor(rightImage, cv2.COLOR_BGR2GRAY)
    grayLeft = cv2.cvtColor(leftImage, cv2.COLOR_RGB2GRAY)

    #dimleft= numpy.shape(grayLeft)
    #dimright = numpy.shape(grayRight)

    #lefth = dimleft[0]
    #leftw = dimleft[1]
    #righth = dimright[0]
    #rightw = dimright[1]

    #print(str(lefth) + " " + str(leftw) + " " + str(righth) + " " + str(rightw) + "\n")


    cv2.imshow('grayLeft', grayLeft)
    cv2.imshow('grayRight', grayRight)


    disparity = stereo_compute.compute(grayLeft, grayRight)
    cv2.imshow('Disparity Map', disparity)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('s'):
        counter = counter + 1
        leftFilename = "calibrationImage" + str(counter) + "L.png"
        rightFilename = "calibrationImage" + str(counter) + "R.png"
        cv2.imwrite(leftFilename, grayLeft)
        cv2.imwrite(rightFilename, grayRight)
        

stereo_camera.release()
cv2.destroyAllWindows()
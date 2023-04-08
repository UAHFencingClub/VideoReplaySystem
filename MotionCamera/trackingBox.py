import numpy

def center(boundingBox):
    centerX = int(boundingBox[0]) + int(boundingBox[2]/2)
    centerY = int(boundingBox[1]) + int(boundingBox[3]/2)
    return centerX, centerY

def movementOfMovingCamera(frameWidth,Fencer1X,Fencer2X):
    moveLeft = 0
    moveRight = 0
    leftBoundry = 50
    rightBoundry = frameWidth - 50

    #fencers are centered in the camera
    if (((Fencer1X < leftBoundry) and (Fencer1X > rightBoundry)) and ((Fencer2X < leftBoundry) and (Fencer2X > rightBoundry))):
        moveLeft = 0
        moveRight = 0
    #F
    elif (((Fencer1X > leftBoundry) and (Fencer1X < rightBoundry)) and ((Fencer2X > leftBoundry) and (Fencer2X < rightBoundry))):
        moveLeft = 1
        moveRight = 0
    elif (((Fencer1X > leftBoundry) and (Fencer1X < rightBoundry)) and ((Fencer2X > leftBoundry) and (Fencer2X < rightBoundry))):
        moveLeft = 0
        moveRight = 1
    elif (((Fencer1X > leftBoundry) and (Fencer1X < rightBoundry)) and ((Fencer2X > leftBoundry) and (Fencer2X < rightBoundry))):
        moveRight = 0
        moveLeft = 0
    return moveLeft, moveRight

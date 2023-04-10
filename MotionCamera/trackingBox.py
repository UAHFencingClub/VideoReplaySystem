import numpy
import socketio
import json
import rel

class CameraMove:
    def __init__(self, url) -> None:
        self.url = url
        self.sio = socketio.Client()
        self.sio.connect(url)
        
    def move(self, yaw, pitch):
        data = {
            "motor_x": yaw/90,
            "motor_y": pitch/90,
        }
        self.sio.emit('my event', data)

def center(boundingBox):
    centerX = int(boundingBox[0]) + int(boundingBox[2]/2)
    centerY = int(boundingBox[1]) + int(boundingBox[3]/2)
    return centerX, centerY

def movementOfMovingCamera(frameWidth,Fencer1X,Fencer2X):
    moveLeft = 0
    moveRight = 0
    leftBoundry = 180
    rightBoundry = frameWidth - 100
    fencer1InMiddle = (Fencer1X > leftBoundry) and (Fencer1X < rightBoundry)
    fencer1Left = Fencer1X < leftBoundry
    fencer1Right = Fencer1X > rightBoundry
    fencer2InMiddle = (Fencer2X > leftBoundry) and (Fencer2X < rightBoundry)
    fencer2Left = Fencer2X < leftBoundry
    fencer2Right = Fencer2X > rightBoundry

    #fencers are centered in the camera
    if (fencer1InMiddle and fencer2InMiddle):
        moveLeft = 0
        moveRight = 0
    # Both fencers at the edge of the frame
    elif ((fencer1Left or fencer1Right) and (fencer2Right or fencer2Left)):
        moveRight = 0
        moveLeft = 0
    # One fencer on the left and the other in the middle
    elif ((fencer2Left or fencer1Left) and (fencer1InMiddle or fencer2InMiddle)):
        moveLeft = 1
        moveRight = 0
    # One fencer on the right and the other in the middle
    elif ((fencer1Right or fencer2Right) and (fencer2InMiddle or fencer1InMiddle)):
        moveLeft = 0
        moveRight = 1
    
    return moveLeft, moveRight

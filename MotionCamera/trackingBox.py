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
        #should be handled on the other end, will do later.
        assert(abs(yaw)<=90)
        assert(pitch<0)
        assert(pitch>=-90)
        data = {
            "motor_x": yaw/90,
            "motor_y": pitch/90,
        }
        self.sio.emit('my event', data)

def center(boundingBox):
    centerX = int(boundingBox[0]) + int(boundingBox[2]/2)
    centerY = int(boundingBox[1]) + int(boundingBox[3]/2)
    return centerX, centerY

def movement(frameWidth,frameHeight,rightFencerX,rightFencerY,leftFencerX,leftFencerY):
    
    
    return moveLeft, moveRight, zoomout, zoomin

import numpy
from websockets.sync.client import connect
import json

class CameraMove:
    def __init__(self, camera_ip) -> None:
        self.ip = camera_ip
        self.websocket = connect("ws://"+camera_ip)

    def move(self, angle):
        assert(abs(angle)<=90)
        event = {
            "type": "my event",
            "motor_x": angle/90,
        }
        self.websocket.send(json.dumps(event))

def center(boundingBox):
    centerX = int(boundingBox[0]) + int(boundingBox[2]/2)
    centerY = int(boundingBox[1]) + int(boundingBox[3]/2)
    return centerX, centerY

def movement(frameWidth,frameHeight,rightFencerX,rightFencerY,leftFencerX,leftFencerY):
    
    
    return moveLeft, moveRight, zoomout, zoomin

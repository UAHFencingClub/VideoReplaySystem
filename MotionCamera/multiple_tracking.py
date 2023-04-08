import time
import cv2
import sys
import numpy
import trackingBox
import socketio
import json
import rel

tracker_types = ['KCF','MOSSE', 'CSRT']
tracker_type = tracker_types[2]

camera_motion = trackingBox.CameraMove("http://10.4.145.139:5000/controller")

#face_detect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#face_detect = cv2.CascadeClassifier('haarcascade_fullbody.xml')


facebox1 = (0,0,0,0)
facebox2 = (0,0,0,0)
initial_find1 = False
initial_find2 = False
trackingFailure1 = 1
trackingFailure2 = 1
centerX1 = 300
centerX2 = 300
centerAngleX = 0
centerAngleY = 3
currentAngle = 0
incrementAngle = 1


if tracker_type == 'KCF':
    TrackerFunction = cv2.TrackerKCF_create
elif tracker_type == 'MOSSE':
    TrackerFunction = cv2.TrackerMOSSE_create
elif tracker_type == "CSRT":
    TrackerFunction = cv2.TrackerCSRT_create

tracker1 = TrackerFunction()
tracker2 = TrackerFunction()


# Starts the video and lets the camera focus for a second
video = cv2.VideoCapture(1) # for using CAM
#video = cv2.VideoCapture("rtsp://10.4.145.139:8554/cam")
time.sleep(1.0)
 
# Exit if video not opened.
if not video.isOpened():
    print("Could not open video")
    sys.exit()

# Read first frame.
ok, frame = video.read()
if not ok:
    print ('Cannot read video file')
    sys.exit()


while True:
    #Read in the frame data 
    ok, frame = video.read()
    #frame = cv2.flip(frame,1)

    # If the frame data cannot be read then exit the tracking loop
    if not ok:
        break
    
    # Getting the time before running the tracking algorithm
    timer = cv2.getTickCount()

    frameWidth  = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    

    key_pressed = cv2.waitKey(1) & 0xFF
    
    # Gets the initial bounding boxes for the faces detected in the frame
    if (key_pressed == ord('s')) or ((initial_find1 == 0) or (initial_find2 == 0)): # runs if the face tracking algorithm
        #Converting the frame to gray tone so that the face detection can work
        #gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        
        #Detecting the faces in the frame
        #faces = face_detect.detectMultiScale(gray_frame,1.1,3)
        faces = cv2.selectROIs("Select Fencers",frame,False)
        #print(faces)
        cv2.destroyWindow("Select Fencers")

        #Checking the number of faces in the frame
        num_faces = numpy.shape(faces)
        # Tracking success
        if num_faces[0] < 1:
            initial_find1 = False
            initial_find2 = False
            camera_motion.move(centerAngleX,centerAngleY)
        elif num_faces[0] < 2:
            facebox1 = (faces[0][0],faces[0][1],faces[0][2],faces[0][3])
            tracker1 = TrackerFunction()
            ok1 = tracker1.init(frame, facebox1)
            initial_find1 = True
        # If there is more than two faces in frame draw bounding boxes for the first two
        else:
            facebox1 = (int(faces[0][0]),int(faces[0][1]),int(faces[0][2]),int(faces[0][3]))
            facebox2 = (int(faces[1][0]),int(faces[1][1]),int(faces[1][2]),int(faces[1][3]))
            tracker1 = TrackerFunction()
            ok1 = tracker1.init(frame, facebox1)
            initial_find1 = True
            tracker2 = TrackerFunction()
            ok2 = tracker2.init(frame, facebox2)
            initial_find2 = True
    elif key_pressed == ord('q'): # if press q 
        break

    # Tracking the first object
    if facebox1 and initial_find1:
        # Tracking success
        trackingFailure1 = 0
        ok1, facebox1 = tracker1.update(frame)
        p1 = (int(facebox1[0]), int(facebox1[1]))
        p2 = (int(facebox1[0] + facebox1[2]), int(facebox1[1] + facebox1[3]))
        centerX1, centerY1 = trackingBox.center(facebox1)
        cv2.rectangle(frame, p1, p2, (0,255,255), 2, 1)
        cv2.line(frame, (centerX1-5, centerY1), (centerX1+5, centerY1), (0,255,255), 1)
        cv2.line(frame, (centerX1, centerY1-5), (centerX1, centerY1+5), (0,255,255), 1)
    else :
        # Tracking failure
        trackingFailure1 = 1
        cv2.putText(frame, "Tracking failure detected on 1", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    # Tracking the second object
    if facebox2 and initial_find2:
        # Tracking success
        trackingFailure2 = 0
        ok2, facebox2 = tracker2.update(frame)
        p1 = (int(facebox2[0]), int(facebox2[1]))
        p2 = (int(facebox2[0] + facebox2[2]), int(facebox2[1] + facebox2[3]))
        centerX2, centerY2 = trackingBox.center(facebox2)
        cv2.rectangle(frame, p1, p2, (255,0,255), 2, 1)
        cv2.line(frame, (centerX2-5, centerY2), (centerX2+5, centerY2), (255,0,255), 1)
        cv2.line(frame, (centerX2, centerY2-5), (centerX2, centerY2+5), (255,0,255), 1)
    else :
        # Tracking failure
        trackingFailure2 = 1
        cv2.putText(frame, "Tracking failure detected on 2", (100,110), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    
    if (trackingFailure1 == 0) and (trackingFailure2 == 0):
        moveLeft, moveRight = trackingBox.movementOfMovingCamera(frameWidth,centerX1,centerX2)
        currentAngle = currentAngle + moveLeft - moveRight
        if(currentAngle < 10) and (currentAngle > -10):
            camera_motion.move(currentAngle,centerAngleY)
        print(frameWidth)
        print(centerX1)
        print(centerX2)
        print(moveRight)
        print(moveLeft)
        



    # Calculate Frames per second (FPS)
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

    #Displaying the tracking algorithm
    cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
    
    # Display FPS on frame
    cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)
        # Display result
    cv2.imshow("Tracking", frame)

video.release()
cv2.destroyAllWindows()
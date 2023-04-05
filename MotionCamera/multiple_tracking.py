import time
import cv2
import sys
import numpy
from trackingBox import center

tracker_types = ['KCF','MOSSE', 'CSRT']
tracker_type = tracker_types[2]

face_detect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Trying the HOG algorithm for person detection
#person = cv2.HOGDescriptor()
#person.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

facebox1 = (0,0,0,0)
facebox2 = (0,0,0,0)
initial_find1 = False
initial_find2 = False

if tracker_type == 'KCF':
    tracker1 = cv2.TrackerKCF_create()
    tracker2 = cv2.TrackerKCF_create()
elif tracker_type == 'MOSSE':
    tracker1 = cv2.TrackerMOSSE_create()
    tracker2 = cv2.TrackerMOSSE_create()
elif tracker_type == "CSRT":
    tracker1 = cv2.TrackerCSRT_create()
    tracker2 = cv2.TrackerCSRT_create()


# Starts the video and lets the camera focus for a second
video = cv2.VideoCapture(0) # for using CAM
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

    # If the frame data cannot be read then exit the tracking loop
    if not ok:
        break
    
    # Getting the time before running the tracking algorithm
    timer = cv2.getTickCount()

    # Gets the initial bounding boxes for the faces detected in the frame
    if cv2.waitKey(1) & 0xFF == ord('s'): # runs if the face tracking algorithm

        #Converting the frame to gray tone so that the face detection can work
        gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        
        #Detecting the faces in the frame
        faces = face_detect.detectMultiScale(gray_frame,1.1,3)
        print(faces)

        #Checking the number of faces in the frame
        num_faces = numpy.shape(faces)
        # Tracking success
        if num_faces[0] < 1:
            initial_find1 = False
            initial_find2 = False
        elif num_faces[0] < 2:
            facebox1 = (faces[0][0],faces[0][1],faces[0][2],faces[0][3])
            tracker1 = cv2.TrackerCSRT_create()
            ok1 = tracker1.init(frame, facebox1)
            initial_find1 = True
        # If there is more than two faces in frame draw bounding boxes for the first two
        else:
            facebox1 = (int(faces[0][0]),int(faces[0][1]),int(faces[0][2]),int(faces[0][3]))
            facebox2 = (int(faces[1][0]),int(faces[1][1]),int(faces[1][2]),int(faces[1][3]))
            tracker1 = cv2.TrackerCSRT_create()
            ok1 = tracker1.init(frame, facebox1)
            initial_find1 = True
            tracker2 = cv2.TrackerCSRT_create()
            ok2 = tracker2.init(frame, facebox2)
            initial_find2 = True

    # Tracking the first object
    if facebox1 and initial_find1:
        # Tracking success
        ok1, facebox1 = tracker1.update(frame)
        p1 = (int(facebox1[0]), int(facebox1[1]))
        p2 = (int(facebox1[0] + facebox1[2]), int(facebox1[1] + facebox1[3]))
        centerX, centerY = center(facebox1)
        cv2.rectangle(frame, p1, p2, (0,255,255), 2, 1)
        cv2.line(frame, (centerX-5, centerY), (centerX+5, centerY), (0,255,255), 1)
        cv2.line(frame, (centerX, centerY-5), (centerX, centerY+5), (0,255,255), 1)
    else :
        # Tracking failure
        cv2.putText(frame, "Tracking failure detected on 1", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    # Tracking the second object
    if facebox2 and initial_find2:
        # Tracking success
        ok2, facebox2 = tracker2.update(frame)
        p1 = (int(facebox2[0]), int(facebox2[1]))
        p2 = (int(facebox2[0] + facebox2[2]), int(facebox2[1] + facebox2[3]))
        centerX, centerY = center(facebox2)
        cv2.rectangle(frame, p1, p2, (255,0,255), 2, 1)
        cv2.line(frame, (centerX-5, centerY), (centerX+5, centerY), (255,0,255), 1)
        cv2.line(frame, (centerX, centerY-5), (centerX, centerY+5), (255,0,255), 1)
    else :
        # Tracking failure
        cv2.putText(frame, "Tracking failure detected on 2", (100,110), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    
    # Calculate Frames per second (FPS)
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

    #Displaying the tracking algorithm
    cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
    
    # Display FPS on frame
    cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)
        # Display result
    cv2.imshow("Tracking", frame)

    #Exiting the tracking loop
    if cv2.waitKey(1) & 0xFF == ord('q'): # if press SPACE bar
        break

video.release()
cv2.destroyAllWindows()
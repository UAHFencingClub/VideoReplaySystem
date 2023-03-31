import argparse
import time
import cv2
import sys
import numpy

#15.
tracker_types = ['KCF','MOSSE', 'CSRT']
tracker_type = tracker_types[2]

face_detect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


facebox1 = (0,0,0,0)
facebox2 = (0,0,0,0)
initial_find1 = False
initial_find2 = False

if tracker_type == 'KCF':
    TrackingFunction = cv2.TrackerKCF_create
elif tracker_type == 'MOSSE':
    TrackingFunction = cv2.TrackerMOSSE_create
elif tracker_type == "CSRT":
    TrackingFunction = cv2.TrackerCSRT_create


#Starts the video and lets the camera focus for a second
video = cv2.VideoCapture(2) # for using CAM
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
        
        facebox1 = cv2.selectROI(frame, False)
        facebox2 = cv2.selectROI(frame, False)
        #Checking the number of faces in the frame
        # Tracking success
        tracker1 = TrackingFunction()
        ok1 = tracker1.init(frame, facebox1)
        initial_find1 = True
        tracker2 = TrackingFunction()
        ok2 = tracker2.init(frame, facebox2)
        initial_find2 = True

    
    if facebox1 and initial_find1:
        # Tracking success
        ok1, facebox1 = tracker1.update(frame)
        p1 = (int(facebox1[0]), int(facebox1[1]))
        p2 = (int(facebox1[0] + facebox1[2]), int(facebox1[1] + facebox1[3]))
        cv2.rectangle(frame, p1, p2, (0,255,255), 2, 1)
    else :
        # Tracking failure
        cv2.putText(frame, "Tracking failure detected on 1", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)


    if facebox2 and initial_find2:
        # Tracking success
        ok2, facebox2 = tracker2.update(frame)
        p1 = (int(facebox2[0]), int(facebox2[1]))
        p2 = (int(facebox2[0] + facebox2[2]), int(facebox2[1] + facebox2[3]))
        cv2.rectangle(frame, p1, p2, (255,0,255), 2, 1)
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
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys


tracker_types = ['KCF','MOSSE', 'CSRT']
tracker_type = tracker_types[0]



if tracker_type == 'KCF':
    tracker = cv2.legacy.TrackerKCF_create()
elif tracker_type == 'MOSSE':
    tracker = cv2.legacy.TrackerMOSSE_create()
elif tracker_type == "CSRT":
    tracker = cv2.legacy.TrackerCSRT_create()

trackers = cv2.legacy.MultiTracker_create()

video = cv2.VideoCapture(1) # for using CAM
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
    ok, frame = video.read()

    if not ok:
        break

    timer = cv2.getTickCount()

    # Update tracker
    #ok, bbox = tracker.update(frame)

    #frame = imutils.resize(frame, 600)

    ok, boxes = trackers.update(frame)

    # Calculate Frames per second (FPS)
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

    for i, box in enumerate(boxes):
        (x,y,w,h) = [int(v) for v in box]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if ok:
            # Tracking success
            p1 = (int(box[0]), int(box[1]))
            p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
            cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
        else :
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
    
    # Display FPS on frame
    cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)
        # Display result
    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'): # if press SPACE bar
        break

    if cv2.waitKey(1) & 0xFF == ord("s"):
        box = cv2.selectROI("selectROI",frame,True,True)
        trackers.add(tracker,frame,box)
        #box = cv2.selectROI("selectROI",frame,False,True)
        #trackers.add(tracker,frame,box)

video.release()
cv2.destroyAllWindows()
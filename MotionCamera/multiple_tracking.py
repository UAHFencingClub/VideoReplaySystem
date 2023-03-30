from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys
import numpy


tracker_types = ['KCF','MOSSE', 'CSRT']
tracker_type = tracker_types[0]

face_detect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#Andrea_face = cv2.CascadeClassifier('Andrea_face.jpg')
facebox1 = (0,0,0,0)
facebox2 = (0,0,0,0)
initial_find1 = False
initial_find2 = False
#ok1 = False

if tracker_type == 'KCF':
    tracker1 = cv2.TrackerKCF_create()
    tracker2 = cv2.TrackerKCF_create()
elif tracker_type == 'MOSSE':
    tracker1 = cv2.TrackerMOSSE_create()
    tracker2 = cv2.TrackerMOSSE_create()
elif tracker_type == "CSRT":
    tracker1 = cv2.TrackerCSRT_create()
    tracker2 = cv2.TrackerCSRT_create()



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

#select initial bounding boxes
#bbox1 = cv2.selectROI(frame, False)
#bbox2 = cv2.selectROI(frame, False)

#ok = tracker1.init(frame, bbox1)
#ok = tracker2.init(frame, bbox2)

while True:
    ok, frame = video.read()

    if not ok:
        break

    #timer = cv2.getTickCount()

    # Update tracker
    #ok1, bbox1 = tracker1.update(frame)
    #ok2, bbox2 = tracker2.update(frame)
    #print(bbox1)
    #print(bbox2)
    #frame = imutils.resize(frame, 600)


    # Calculate Frames per second (FPS)
    #fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

    if cv2.waitKey(1) & 0xFF == ord('1'): # if press SPACE bar
        gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces = face_detect.detectMultiScale(gray_frame,1.1,3)
        print(faces)
        num_faces = numpy.shape(faces)
        # Tracking success
        if num_faces[0] < 2:
            facebox1 = (faces[0][0],faces[0][1],faces[0][2],faces[0][3])
            #p1 = (int(facebox1[0]), int(facebox1[1]))
            #p2 = (int(facebox1[0] + facebox1[2]), int(facebox1[1] + facebox1[3]))
            #cv2.rectangle(frame, p1, p2, (255,0,255), 2, 1)
            tracker1 = cv2.TrackerKCF_create()
            ok1 = tracker1.init(frame, facebox1)
            initial_find1 = True
        else:
            facebox1 = (int(faces[0][0]),int(faces[0][1]),int(faces[0][2]),int(faces[0][3]))
            facebox2 = (int(faces[1][0]),int(faces[1][1]),int(faces[1][2]),int(faces[1][3]))
            tracker1 = cv2.TrackerKCF_create()
            ok1 = tracker1.init(frame, facebox1)
            initial_find1 = True
            tracker2 = cv2.TrackerKCF_create()
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

    #ok2 = False
    #if ok2:
        # Tracking success
     #   p1 = (int(bbox2[0]), int(bbox2[1]))
      #  p2 = (int(bbox2[0] + bbox2[2]), int(bbox2[1] + bbox2[3]))
       # cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
    #else :
        # Tracking failure
    #    cv2.putText(frame, "Tracking failure detected on 2", (100,110), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
    

    cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
    
    # Display FPS on frame
    #cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)
        # Display result
    cv2.imshow("Tracking", frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'): # if press SPACE bar
        break

video.release()
cv2.destroyAllWindows()
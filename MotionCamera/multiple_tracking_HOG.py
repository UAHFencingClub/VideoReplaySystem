import time
import cv2
import sys
import numpy
from trackingBox import center


tracker_types = ['KCF','MOSSE', 'CSRT']
tracker_type = tracker_types[0]

# Trying the HOG algorithm for person detection
person = cv2.HOGDescriptor()
person.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

facebox1 = (0,0,0,0)
facebox2 = (0,0,0,0)
initial_find1 = False
initial_find2 = False


if tracker_type == 'KCF':
    TrackerFunction = cv2.TrackerKCF_create
elif tracker_type == 'MOSSE':
    TrackerFunction = cv2.TrackerMOSSE_create
elif tracker_type == "CSRT":
    TrackerFunction = cv2.TrackerCSRT_create

tracker1 = TrackerFunction()
tracker2 = TrackerFunction()


# Starts the video and lets the camera focus for a second
video = cv2.VideoCapture('test_video.mp4') # for using CAM
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
    frame = cv2.resize(frame, (640, 480))

    # If the frame data cannot be read then exit the tracking loop
    if not ok:
        break
    
    #width  = video.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    #height = video.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

    # Getting the time before running the tracking algorithm
    timer = cv2.getTickCount()

    key_pressed = cv2.waitKey(1) & 0xFF

    # Gets the initial bounding boxes for the people detected in the frame
    if key_pressed == ord('s'): # runs if the face tracking algorithm
        
        # Setting up the the HOG detection algorithm
        people, weights = person.detectMultiScale(frame,1,[16,16],[8,8],1.15,0)
        print(people)
        print(weights)

        #Checking the number of people in the frame
        num_people = numpy.shape(people)
        # Tracking success
        if num_people[0] < 1:
            initial_find1 = False
            initial_find2 = False
        elif num_people[0] < 2:
            facebox1 = (people[0][0],people[0][1],people[0][2],people[0][3])
            tracker1 = TrackerFunction()
            ok1 = tracker1.init(frame, facebox1)
            initial_find1 = True
        # If there is more than two people in frame draw bounding boxes for the first two
        else:
            facebox1 = (int(people[0][0]),int(people[0][1]),int(people[0][2]),int(people[0][3]))
            tracker1 = TrackerFunction()
            ok1 = tracker1.init(frame, facebox1)
            initial_find1 = True
            facebox2 = (int(people[1][0]),int(people[1][1]),int(people[1][2]),int(people[1][3]))
            tracker2 = TrackerFunction()
            ok2 = tracker2.init(frame, facebox2)
            initial_find2 = True
    #Exiting the tracking loop
    elif key_pressed == ord('q'): # if press q 
        break

    # Tracking the first object
    if facebox1 and initial_find1:
        # Tracking success
        ok1, facebox1 = tracker1.update(frame)
        p1 = (int(facebox1[0]), int(facebox1[1]))
        p2 = (int(facebox1[0] + facebox1[2]), int(facebox1[1] + facebox1[3]))
        centerX, centerY = center(facebox1)


        cv2.rectangle(frame, p1, p2, (0,255,255), 2, 1)
        cv2.line(frame, (centerX-5, centerY), (centerX+5, centerY), (0,255,255), 2)
        cv2.line(frame, (centerX, centerY-5), (centerX, centerY+5), (0,255,255), 2)
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
        cv2.line(frame, (centerX-5, centerY), (centerX+5, centerY), (255,0,255), 2)
        cv2.line(frame, (centerX, centerY-5), (centerX, centerY+5), (255,0,255), 2)
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

video.release()
cv2.destroyAllWindows()
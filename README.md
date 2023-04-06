Still a WIP project, more documentaion will come as we submit our final report.


#Design Problem

Video replay systems are used in fencing tournaments to aid in the scoring of a bout, or fencing match, and to train both athletes and referees. However, the footage and recordings available are often hard to find, and when available, the quality is poor with jerky camera movements, due to human control, and unintelligible referee audio as prime examples.


#Design Concept

Our goal is to create a camera that can automatically pan, tilt, and zoom to keep the athletes in frame in a smooth fashion. The system will also incorporate a separate audio stream from the referee in the media stream.


#Summary Of Design Approach

A USB webcam is used to track the fencers as they move on the piste during the match. The tracking software will use (type of tracking algorithm) to create a bounding box around the fencers that will send data to the Raspberry Pi that controls the main video camera. The Webcam has a field of view (FOV) of 78°, and as fencers near the edge of the frame the camera will move to keep them in frame. There will also be a webserver that will allow for video streaming and recording of the fencing matches. Scoring and referee audio will also be viewable in the media stream.


#Main Features of The Design

- The project uses a Raspberry Pi 4 to run the tracking software as well as the Webserver for video streaming and recording. 
- The Arducam PTZ camera is used as the video camera that will track and record the fencers during the match. The camera has pan, tilt, and zoom capabilities, and provides 720p video at 30fps.
- The Mounting system for the camera is composed of a standard 5 foot tripod and a custom 3-D printed mount for the camera. The camera mount was printed using PLA filament.
- A Logitech C920s USB webcam is used to track the fencers using the object tracking software.
- The scoring machine for the fencing match is integrated into the media stream using a Wi-Fi development board to transmit the data from the scoring machine to the Raspberry Pi 4.

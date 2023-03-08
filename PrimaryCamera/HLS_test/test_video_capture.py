#!/usr/bin/python3
import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from picamera2.outputs import CircularOutput
from picamera2.outputs import FileOutput
from libcamera import Transform

picam2 = Picamera2()
video_config = picam2.create_video_configuration(raw={"size": (1280, 720)},transform=Transform(hflip=True,vflip=True))
#video_config["controls"]['FrameDurationLimits']=(25000,25000)

picam2.configure(video_config)
picam2.set_controls({"FrameRate": 40})

encoder = H264Encoder(10000000)
#output = FfmpegOutput('test.mp4', audio=True)
output1 = FfmpegOutput("-f hls -hls_time 4 -hls_list_size 20 -hls_flags delete_segments -hls_allow_cache 0 stream.m3u8")
output2 = FileOutput()
output3 = CircularOutput()
output3.fileoutput = "file.h264"
encoder.output = [output1, output2, output3]

#picam2.start_recording(encoder, output)

# Start streaming to the network.
picam2.start_encoder(encoder)
picam2.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    output3.start()
    time.sleep(5)
    output3.stop()
    print('interrupted!')

print('Stopping Encoder')
picam2.stop_encoder()

print('Stopping')
#picam2.stop_recording()
for output in encoder.output:
    output.stop()
picam2.stop()

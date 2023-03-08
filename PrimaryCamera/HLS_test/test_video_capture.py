#!/usr/bin/python3
import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

picam2 = Picamera2()
video_config = picam2.create_video_configuration()
picam2.configure(video_config)

encoder = H264Encoder(10000000)
#output = FfmpegOutput('test.mp4', audio=True)
output = FfmpegOutput("-f hls -hls_time 4 -hls_list_size 20 -hls_flags delete_segments -hls_allow_cache 0 stream.m3u8")

picam2.start_recording(encoder, output)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('interrupted!')

picam2.stop_recording()

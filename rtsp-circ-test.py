# primarilly based on [1] https://www.appsloveworld.com/bestanswer/raspberry-pi/11/how-do-i-buffer-and-capture-an-rtsp-stream-to-disk-based-on-a-trigger
# [2] https://stackoverflow.com/questions/75425406/creating-video-from-images-using-pyav
import av
import time
import queue
from threading import Thread, Event
from getkey import getkey, keys
import itertools
from collections import deque


class CircularRTSPRecorder(Thread):

    def __init__(self, source_url: str = "", sink_url: str = ""):
        Thread.__init__(self)
        self.source_url = source_url
        self.sink_url = sink_url
        self.av_instance = None
        self.connected = False
        self.frame_buffer = deque('',maxlen=1000)
        self.record_event = Event()

    def open_rtsp_stream(self):
        try:
            self.video_source = av.open(self.source_url, 'r')
            self.video_sink = av.open(self.sink_url, 'w')
            self.connected = True
            print ("Connected")
        except av.error.HTTPUnauthorizedError:
            print ("aHTTPUnauthorizedError")
        except Exception as Error:
            # Catch other pyav errors if you want, just for example
            print (Error)

        # [2]
        in_stream = self.video_source.streams.video[0]
        codec_name = in_stream.codec_context.name  # Get the codec name from the input video stream.
        #fps = in_stream.codec_context.rate  # Get the framerate from the input video stream.
        fps = 30 #Assuming that I cant get that data from an rtsp stream
        self.out_stream = self.video_sink.add_stream(codec_name, str(fps))
        self.out_stream.width = in_stream.codec_context.width  # Set frame width to be the same as the width of the input stream
        self.out_stream.height = in_stream.codec_context.height  # Set frame height to be the same as the height of the input stream
        self.out_stream.pix_fmt = in_stream.codec_context.pix_fmt

    def run(self):
        self.open_rtsp_stream()

        while 1:
            if self.connected:
                for packet in self.video_source.demux():
                    for frame in packet.decode():
                        if packet.stream.type == 'video':
                            self.frame_buffer.append(frame)

                        if self.record_event.is_set():
                            for frame in self.frame_buffer:
                                # [2]
                                img_frame = frame.to_image()
                                out_frame = av.VideoFrame.from_image(img_frame)  # Note: to_image and from_image is not required in this specific example.
                                out_packet = self.out_stream.encode(out_frame)  # Encode video frame
                                self.video_sink.mux(out_packet)  # "Mux" the encoded frame (add the encoded frame to MP4 file).
                            
                            # Flush the encoder
                            out_packet = self.out_stream.encode(None)
                            self.video_sink.mux(out_packet)
                            self.video_sink.close()
                            print("Saved and Closed")
            else:
                time.sleep(10)

recorder = CircularRTSPRecorder(source_url='rtsp://192.168.9.153:8554/cam',sink_url="test.mp4")
recorder.start()

while True:
    key = getkey()
    if key == 'a':
        print('test')
    elif key == 'b':
        print('save')
        recorder.record_event.set()
    elif key == 'q':
        print("TODO")

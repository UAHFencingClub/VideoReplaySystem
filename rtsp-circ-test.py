#https://www.appsloveworld.com/bestanswer/raspberry-pi/11/how-do-i-buffer-and-capture-an-rtsp-stream-to-disk-based-on-a-trigger
import av
import time
import queue
from threading import Thread, Event


class LightingRecorder(Thread):

    def __init__(self, source: str = ""):
        Thread.__init__(self)
        self.source = source
        self.av_instance = None
        self.connected = False
        self.frame_buffer = queue.Queue()
        self.record_event = Event()

    def open_rtsp_stream(self):
        try:
            self.av_instance = av.open(self.source, 'r')
            self.connected = True
            print ("Connected")
        except av.error.HTTPUnauthorizedError:
            print ("aHTTPUnauthorizedError")
        except Exception as Error:
            # Catch other pyav errors if you want, just for example
            print (Error)

    def run(self):
        self.open_rtsp_stream()

        while 1:
            if self.connected:
                for packet in self.av_instance.demux():
                    for frame in packet.decode():
                        if packet.stream.type == 'video':
                            # TODO:
                            # Handle clearing of Framebuffer, remove frames that are older as a specific timestamp
                            # Or calculate FPS per seconds and store that many frames on framebuffer
                            print ("Add Frame to framebuffer", frame)
                            self.frame_buffer.put(frame)

                        if self.record_event.is_set():
                            [frame.to_image().save('frame-%04d.jpg' % frame.index) for frame in self.frame_buffer]
            else:
                time.sleep(10)

LightingRecorder(source='rtsp://192.168.9.153:8554/cam').start()
from flask import Flask, request, render_template, send_from_directory, Response, redirect
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput, CircularOutput, FileOutput
from libcamera import Transform
import cv2
import numpy as np
import os
import subprocess, shlex
from flask_socketio import SocketIO, emit


app = Flask(__name__)
socketio = SocketIO(app)

if app.config["ENV"] == "development":
	from FocuserDummy import Focuser as CameraController
else:
	from CameraController import CameraController

app.config['TEMPLATES_AUTO_RELOAD'] = True

camera_control = CameraController()


YOUTUBE_URL = os.environ.get('YOUTUBE_URL')
YOUTUBE_KEY = os.environ.get('KEY')


picam2 = Picamera2()
video_config = picam2.create_video_configuration(raw={"size": (1280, 720)},transform=Transform(hflip=True,vflip=True))
#video_config["controls"]['FrameDurationLimits']=(25000,25000)

picam2.configure(video_config)
picam2.set_controls({"FrameRate": 40})

encoder = H264Encoder(10000000)
output1 = FfmpegOutput("-f mpegts udp://192.168.9.154:1234",audio=True)
#output_yt = FfmpegOutput(f"-re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv rtmp://a.rtmp.youtube.com/live2/{YOUTUBE_KEY}")
output2 = FileOutput('full.h264')
output3 = CircularOutput(buffersize=3000)
encoder.output = [output1, output2, output3]

# Start streaming to the network.
picam2.start_encoder(encoder)
#The encoder automatically calls output.start()
output2.stop()
output3.stop()
picam2.start()



@app.route('/')
def index():
	return 'Server Works!'

REPLAY_CLIPS_DIRECTORY='clips'
REPLAY_CLIPS_FORMAT='mp4'
@app.route(f'/{REPLAY_CLIPS_DIRECTORY}/<path:path>')
def get_replay_clip(path):
	return send_from_directory(REPLAY_CLIPS_DIRECTORY,path)

@app.route('/images/<path:path>')
def get_image(path):
	return send_from_directory('images',path)

@app.route('/replay', methods=['GET', 'POST'])
def replay():
	clip_id =  request.args.get('clip_id') 
	if request.method == 'POST':
		epoch = int(time.time())
		replay_base_filename = f'Replay-{epoch}'
		output3.fileoutput = f"{REPLAY_CLIPS_DIRECTORY}/{replay_base_filename}.h264"
		output3.start()
		output3.stop()
		#TODO implement audio buffer to dump
		#Plan is to use a python queue and a thread to wirite audio to, and itertools to get the last few items in the queue.
		''' Example for my reference
			>>> import itertools
			>>> from collections import deque
			>>> q = deque('',maxlen=10)
			>>> for i in range(10,20):
			...     q.append(i)
			... 
			>>> q
			deque([10, 11, 12, 13, 14, 15, 16, 17, 18, 19], maxlen=10)
			>>> output = list(itertools.islice(q,7,10))
			>>> output
			[17, 18, 19]
			>>> q
			deque([10, 11, 12, 13, 14, 15, 16, 17, 18, 19], maxlen=10)
		'''
		
		ffmpeg_encode_command = shlex.split(f"ffmpeg -i ./{REPLAY_CLIPS_DIRECTORY}/{replay_base_filename}.h264 -c:v copy ./{REPLAY_CLIPS_DIRECTORY}/{replay_base_filename}.{REPLAY_CLIPS_FORMAT}")
		#needs better error handling
		subprocess.run(ffmpeg_encode_command,timeout=30,check=True)

		result = redirect(f"/replay?clip_id={replay_base_filename}.{REPLAY_CLIPS_FORMAT}", code=301)
	elif clip_id is None:
		clips_list = [clip for clip in os.listdir(f"./{REPLAY_CLIPS_DIRECTORY}") if clip.endswith(f".{REPLAY_CLIPS_FORMAT}")]
		result = render_template('replay_list.html',clips_list=clips_list, clip_path = REPLAY_CLIPS_DIRECTORY)
	else: 
		result = render_template('replay_interface.html',clip_id = clip_id, clip_path = REPLAY_CLIPS_DIRECTORY)
	
	return result

def gen():
	while True:
		bgra_frame = picam2.capture_array("main")
		rgb_frame = cv2.cvtColor(bgra_frame, cv2.COLOR_BGRA2RGB )
		_, jpeg_encoded = cv2.imencode('.jpg', rgb_frame)
		data_encode = np.array(jpeg_encoded)
		byte_encode = data_encode.tobytes()
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + byte_encode + b'\r\n')

@app.route('/live_mjpeg')
def mjpeg_live():
    return render_template('mjpeg_live.html')

@app.route('/video_feed')
def video_feed():
	return Response(gen(),
					mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/live')
def live():
	return render_template('live_feed.html')

@app.route('/streams/<path:path>')
def send_streams(path):
	return send_from_directory('streams', path)

@app.route('/api/servo', methods=['GET', 'POST'])
def server_controller():
	result = {"lol":"lmao"}
	if request.method == 'POST':
		content = request.json
		servo.value = content["value"]

	elif request.method == 'GET':
		result = render_template('servo_test_ui.html')

	return result

@app.route('/controller')
def controller_ui():
	"""Builds a Web UI for controlling the camera by sending post requests"""

	return render_template("controller_ui.html",camera_control=camera_control)

@app.route("/socket_test")
def socket_test():
	return render_template("socket_io_test.html")

@app.route("/score")
def display_score():
	return render_template("scoring_display.html")

@socketio.on('my event')
def handle_my_custom_event(json):
	for key in json:
		camera_control.set(key,json[key])

@socketio.on('scoring_update')
def handle_scoreing_update(json):
	print(json)
	emit('scoring_ui_update', json, broadcast=True)

@app.route('/api/camera', methods=['GET', 'POST'])
def camera_api():
	result = {}
	if request.method == 'POST':
		content = request.json
		for key in content:
			if not camera_control.set(key,content[key]):
				return 'Invalid Key: {}'.format(key), 400

	elif request.method == 'GET':
		print("CTL ", camera_control.control_elements)
		for element in camera_control.control_elements:
			result[element] = camera_control.get(element)

	return result

if __name__ == '__main__':
    socketio.run(app)
# print('Stopping Encoder')
# picam2.stop_encoder()

# print('Stopping')
# #picam2.stop_recording()
# for output in encoder.output:
#	 output.stop()
# picam2.stop()

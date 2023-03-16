from flask import Flask, request, render_template, send_from_directory, Response, redirect
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput, CircularOutput, FileOutput
from libcamera import Transform
import cv2
import numpy as np
import os

app = Flask(__name__)

if app.config["ENV"] == "development":
	from FocuserDummy import Focuser as CameraController
else:
	from CameraController import CameraController

camera_control = CameraController()



picam2 = Picamera2()
video_config = picam2.create_video_configuration(raw={"size": (1280, 720)},transform=Transform(hflip=True,vflip=True))
#video_config["controls"]['FrameDurationLimits']=(25000,25000)

picam2.configure(video_config)
picam2.set_controls({"FrameRate": 40})

encoder = H264Encoder(10000000)
#output = FfmpegOutput('test.mp4', audio=True)
output1 = FfmpegOutput("-f hls -hls_time 4 -hls_list_size 20 -hls_flags delete_segments -hls_allow_cache 0 streams/stream.m3u8")
output2 = FileOutput('full.h264')
output3 = CircularOutput()
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

REPLAY_CLIPS_DIRECTORY='/clips'
REPLAY_CLIPS_FORMAT='mp4'
@app.route(f'{REPLAY_CLIPS_DIRECTORY}/<path:path>')
def get_replay_clip(path):
	return send_from_directory('clip',path)

@app.route('/replay/<id>', methods=['GET', 'POST'])
def replay(clip_id):
	if request.method == 'POST':
		epoch = int(time.time())
		replay_base_filename = f'Replay-{epoch}'
		output3.fileoutput = f"./{REPLAY_CLIPS_DIRECTORY}/{replay_base_filename}.h264"
		output3.start()
		output3.stop()
		#TODO implement audio buffer to dump
		#TODO Start background ffmpeg task to convert to mp4
		result = redirect(f"/replay/{replay_base_filename}.{REPLAY_CLIPS_FORMAT}", code=301)
	elif clip_id is None:
		clips_list = [clip for clip in os.listdir(f"./{REPLAY_CLIPS_DIRECTORY}") if clip.endswith(f".{REPLAY_CLIPS_FORMAT}")]
		result = render_template('replay_list.html',clips_list=clips_list, clip_path = REPLAY_CLIPS_DIRECTORY)
	else: 
		result = render_template('replay_interface.html',clip_id = clip_id, clip_path = REPLAY_CLIPS_DIRECTORY)
	
	return result

def gen():
	while True:
		yuv_frame = picam2.capture_array("main")
		rgb_frame = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV420p2RGB)
		_, jpeg_encoded = cv2.imencode('.jpg', rgb_frame)
		data_encode = np.array(jpeg_encoded)
		byte_encode = data_encode.tobytes()
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + byte_encode + b'\r\n')

@app.route('/live_mjpeg')
def index():
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


# print('Stopping Encoder')
# picam2.stop_encoder()

# print('Stopping')
# #picam2.stop_recording()
# for output in encoder.output:
#	 output.stop()
# picam2.stop()
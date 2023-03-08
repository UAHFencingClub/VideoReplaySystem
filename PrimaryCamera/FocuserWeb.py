from flask import Flask, request, render_template, send_from_directory
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput, CircularOutput, FileOutput
from libcamera import Transform

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
output3.fileoutput = "circ.h264"
encoder.output = [output1, output2, output3]

# Start streaming to the network.
picam2.start_encoder(encoder)
picam2.start()


@app.route('/')
def index():
	return 'Server Works!'

@app.route('/replay', methods=['GET', 'POST'])
def replay():
	if request.method == 'POST':
		output3.start()
		output3.stop()
		result = "circ.h264"
	else:
		result = "ToDo"
	
	return result

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
#     output.stop()
# picam2.stop()
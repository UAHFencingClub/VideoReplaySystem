from flask import Flask, request, render_template

app = Flask(__name__)

if app.config["ENV"] == "development":
	from FocuserDummy import Focuser as CameraController
else:
	from CameraController import CameraController

camera_control = CameraController()

@app.route('/')
def index():
	return 'Server Works!'

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



from flask import Flask, request, render_template

app = Flask(__name__)

if app.config["ENV"] == "development":
	from FocuserDummy import Focuser
else:
	from Focuser import Focuser
	
from gpiozero import Servo

servo = Servo(16)

i2c_bus = 1
focuser = Focuser(i2c_bus)

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

	return render_template("controller_ui.html",focuser=focuser)

@app.route('/api/camera', methods=['GET', 'POST'])
def camera_control():
	result = {}
	if request.method == 'POST':
		content = request.json
		for key in content:
			if not focuser.set(key,content[key]):
				return 'Invalid Key: {}'.format(key), 400

	elif request.method == 'GET':
		for opt in Focuser.opts:
			result[opt] = focuser.get(opt)

	return result



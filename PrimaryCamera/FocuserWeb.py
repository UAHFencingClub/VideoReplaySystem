from flask import Flask, request, render_template, send_from_directory, Response, redirect
from flask_socketio import SocketIO, emit


app = Flask(__name__)
socketio = SocketIO(app)

if app.config["ENV"] == "development":
	from FocuserDummy import Focuser as CameraController
else:
	from CameraController import CameraController

app.config['TEMPLATES_AUTO_RELOAD'] = True

camera_control = CameraController()



@app.route('/')
def index():
	return render_template('index.html')

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
	return render_template('replay_feed.html')

@app.route('/live')
def live():
	return render_template('live_feed.html')

@app.route('/controller')
def controller_ui():
	"""Builds a Web UI for controlling the camera by sending post requests"""
	return render_template("controller_ui.html",camera_control=camera_control)

@app.route("/score")
def display_score():
	return render_template("scoring_display.html")



@socketio.on('my event')
def handle_my_custom_event(json):
	for key in json:
		result = camera_control.set(key,json[key])
		emit('my event',result)

@socketio.on('scoring_update')
def handle_scoreing_update(json):
	print(json)
	emit('scoring_ui_update', json, broadcast=True)

@socketio.on('scoring_ui_update',namespace="/score")
@app.route('/api/score',methods=['POST'])
def score_api():
	if request.method == 'POST':
		content = request.json
		emit('scoring_ui_update', content, broadcast=True, namespace="/score")
	return ('', 204)


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
    socketio.run(app, host='0.0.0.0', allow_unsafe_werkzeug=True)

from flask import Flask, request, render_template, send_from_directory, Response, redirect
import time
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
	clip_id = request.args.get('clip_id') 
	if request.method == 'POST':
		time_string = time.strftime("%Y-%m-%d_%H%M%S", time.localtime(time.time()))
		replay_base_filename = f'Replay-{time_string}'
		clip_file = f"{REPLAY_CLIPS_DIRECTORY}/{replay_base_filename}.h264"
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

		result = redirect(f"/replay?clip_id={replay_base_filename}.{REPLAY_CLIPS_FORMAT}", code=301)
	elif clip_id is None:
		clips_list = [clip for clip in os.listdir(f"./{REPLAY_CLIPS_DIRECTORY}") if clip.endswith(f".{REPLAY_CLIPS_FORMAT}")]
		result = render_template('replay_list.html',clips_list=clips_list, clip_path = REPLAY_CLIPS_DIRECTORY)
	else: 
		result = render_template('replay_interface.html',clip_id = clip_id, clip_path = REPLAY_CLIPS_DIRECTORY)
	
	return result

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
    socketio.run(app)

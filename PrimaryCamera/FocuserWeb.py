from flask import Flask, request, render_template
from FocuserDummy import Focuser
app = Flask(__name__)

i2c_bus = 1
focuser = Focuser(i2c_bus)

@app.route('/')
def index():
	return 'Server Works!'

@app.route('/controller')
def controller_ui():
	"""Builds a Web UI for controlling the camera by sending post requests"""
	result = '''
		<!doctype html>
		<div id="camera_control">
	'''

	for opt, value in focuser.opts.items():
		result += '''
			<div id="{div_id}">
				<input type="range" min="{min}" max="{max}" value="{val}" class="slider" id="{div_id}_slider">
				<p>{div_id}: <span id="{div_id}_value"></span></p>
			</div>
		'''.format(div_id = opt, min = value["MIN_VALUE"], max = value["MAX_VALUE"], val=0)

	result += '''
		</div>

		<script>
			let divs = document.querySelectorAll('div')

			divs.forEach((div) => {
				const textNode = document.createTextNode("text")
				var div_slider = div.querySelectorAll('.slider')[0];
				div_slider.oninput = function(test) {
					div.querySelectorAll('span')[0].innerHTML = div_slider.value;
				}
			});
		</script>
	'''

	return result

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



#!/usr/bin/env python3
#From: https://blog.miguelgrinberg.com/post/video-streaming-with-flask modified for our use
from flask import Flask, render_template, Response
import cv2
import numpy as np

webcam = cv2.VideoCapture(0)
if not webcam.isOpened():
    print("Cannot open camera")
    exit()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        global webcam
        ret, frame = webcam.read()
        if not ret:
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n\r\n')
        _, jpeg_encoded = cv2.imencode('.jpg', frame)
        data_encode = np.array(jpeg_encoded)
        byte_encode = data_encode.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_encode + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, use_reloader=False)
    webcam.release()
    print("Quit")
    

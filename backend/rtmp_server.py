import time
import subprocess
import cv2
import socket
from flask import Flask, jsonify
from threading import Thread
import squat_analyser as sa2


# TODO: figure out how to make opencv open the stream / demo on another computer to see speeds

# TODO: implement button in app to intialise this server or,
    # allow this server to be constantly running and not require simultaneous start

# Declare constants for server and commands
port = 8080
ip = socket.gethostbyname(socket.gethostname())
video_stream_input = f'rtmp://{ip}:1935/form_analyser/22022001'
local_rtmp_endpoint = 'rtmp://localhost/live'
ffmpeg_args = ['ffmpeg', '-flags', 'low_delay', '-re', '-f', 'flv', '-listen', '1', '-i', video_stream_input, '-copyts', '-fps_mode', '1', '-preset', 'ultrafast', '-c', 'copy', '-f', 'flv', '-listen', '1', local_rtmp_endpoint]

# Pre-ready video capture object
cap = cv2.VideoCapture()

# Create analysis object
form_analyser = sa2.SquatFormAnalyser()

app = Flask(__name__)
feedback = []

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/form-feedback', methods=['GET'])
def get_form_feedback():
    global feedback
    return jsonify(feedback)

def run_flask_app():
    app.run(host=ip, port=5000)

flask_thread = Thread(target=run_flask_app)
flask_thread.start()

# Begin forwarding rtmp stream to a local endpoint
proc1 = subprocess.Popen(ffmpeg_args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
time.sleep(5)

# Read the local rtmp stream
cap.open(local_rtmp_endpoint)

if not cap.isOpened():
    print('Stream not open')
    proc1.terminate()
    exit()

# implement threading?
    # thread1 grabs frame if prev frame is processed or empty
    # thread2 processes frame

prev_f = []
while True:
    # Process the frame
    immediate_f, suc = form_analyser.analyse(
        cap,
        show_output=False
    )
    if not suc:
        break

    if prev_f != immediate_f:
        if len(immediate_f) > 0 and immediate_f != ['Not Detected'] and immediate_f != ['Insufficient Joint Data']:
            print('Form Feedback:', immediate_f)

        feedback = immediate_f
        prev_f = immediate_f


cv2.destroyAllWindows()
cap.release()
proc1.terminate()

# Do then send a final summary of workout?
# Or make it simultaneously record video for post-processing?

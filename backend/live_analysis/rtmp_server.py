import logging
import socket
import subprocess
import time
from threading import Thread

import cv2
import squat_analyser as sa
from flask import Flask, jsonify


# TODO: final summary of workout? Or make it simultaneously record video for post-processing?

NORMAL = '\u001b[0m'
YELLOW_BG = '\u001b[43m'


# Declare constants for rtmp stream
ip = socket.gethostbyname(socket.gethostname())
cap = cv2.VideoCapture()
video_stream_input = f'rtmp://{ip}:1935/form_analyser/22022001'
local_rtmp_endpoint = 'rtmp://localhost/live'
ffmpeg_args = [
    'ffmpeg',
    '-fflags', 'nobuffer',
    '-flags', 'low_delay',
    '-an',  # Ignore audio
    '-f', 'flv',
    '-listen', '1',
    '-i', video_stream_input,
    '-copyts',
    '-fps_mode', 'cfr',  # Ensure that video frames are synchronized
    '-r', '10',  # Set the output frame rate to 10 FPS # TODO: get this based in input stream
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    '-f', 'flv',
    '-listen', '1',
    local_rtmp_endpoint
]


# Declare constants and variables for feedback
form_analyser = sa.SquatFormAnalyser(use_advanced_criteria=True)
port = 5000
current_f = []


# Create feedback server
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/form-feedback', methods=['GET'])
def get_form_feedback():
    global current_f
    json_f = jsonify(current_f)
    current_f = []
    return json_f

def run_flask_app():
    app.run(host=ip, port=port)
flask_thread = Thread(target=run_flask_app)
flask_thread.daemon = True
flask_thread.start()


# TODO: put this into a request e.g. /start-server and in component add request to endpoint?

# Begin re-streaming to a local endpoint
proc1 = subprocess.Popen(
    ffmpeg_args,
    stdout=subprocess.DEVNULL, # Hide output so we can just see form data
    stderr=subprocess.STDOUT
)
time.sleep(3) # Allow server to start before opening rtmp stream


# Read the local rtmp stream
cap.open(local_rtmp_endpoint)

if not cap.isOpened():
    print('Stream not open')
    cap.release()
    proc1.terminate()
    exit()
print('Stream started!')

try:
    while True:
        # Process the frame
        immediate_f, success = form_analyser.analyse(cap, show_output=False)
        if not success:
            break

        # TODO: change this to append feedback to current_f and then /form-feedback method clears it

        # NOTE: comment this bit out in real testing for performance reasons
        if immediate_f not in [[], current_f]:
            for f in immediate_f:
                if f['tag'] in ['FEEDBACK', 'STATE_SEQUENCE']:
                    print(f'{f["tag"]}: {f["message"]}')
                elif f['tag'] == 'SET_ENDED':
                    print(f'{YELLOW_BG} Final Summary: {f["summary"]}')
                else:
                    print(f'{YELLOW_BG} {f["tag"]}: {f["message"]} {NORMAL}')

        current_f = immediate_f

except KeyboardInterrupt:
    print('Exiting gracefully...')


cv2.destroyAllWindows()
cap.release()
proc1.terminate()

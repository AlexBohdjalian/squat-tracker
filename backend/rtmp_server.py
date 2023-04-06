import logging
import socket
import subprocess
import time
from threading import Thread

import cv2
import squat_analyser as sa
from flask import Flask, jsonify


# TODO: review the live low latency stream to see the quality
# TODO: figure out how to make opencv open the stream / demo on another computer to see speeds
# TODO: implement button in app to intialise this server or, allow this server to be constantly running and not require simultaneous start
# TODO: implement threading?
    # thread1 grabs frame if prev frame is processed or empty
    # thread2 processes frame
# TODO: final summary of workout? Or make it simultaneously record video for post-processing?


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
    '-r', '10',  # Set the output frame rate to 10 FPS
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    '-f', 'flv',
    '-listen', '1',
    local_rtmp_endpoint
]
# ffmpeg_args = [
#     'ffmpeg',
#     '-flags', 'low_delay',
#     '-re',
#     '-f', 'flv',
#     '-listen', '1',
#     '-i', video_stream_input,
#     '-copyts',
#     '-fps_mode', '1',
#     '-preset', 'ultrafast',
#     '-c', 'copy',
#     '-f', 'flv',
#     '-listen', '1',
#     local_rtmp_endpoint
# ]


# Declare constants and variables for feedback
form_analyser = sa.SquatFormAnalyser()
port = 5000
current_f = []


# Create feedback server
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/form-feedback', methods=['GET'])
def get_form_feedback():
    global current_f
    return jsonify(current_f)

def run_flask_app():
    app.run(host=ip, port=port)
flask_thread = Thread(target=run_flask_app)
flask_thread.daemon = True
flask_thread.start()


# TODO: put this into a request e.g. /start-server and in component,
    # add request to handleStreaming
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
        immediate_f, suc = form_analyser.analyse(
            cap,
            show_output=False
        )

        # Break if stream has ended
        if not suc:
            break

        # Logging
        if immediate_f not in [[], current_f]:
            for tag, f in immediate_f:
                if tag == 'STATE_SEQUENCE':
                    print('State Sequence:', f)
                elif tag == 'FEEDBACK' and \
                    f not in ['Not Detected', 'Insufficient Joint Data']:
                    print('Form Feedback:', f)
                else:
                    print('Unhandled Case:', tag, f)

        current_f = immediate_f

except KeyboardInterrupt:
    print('Exiting gracefully...')


cv2.destroyAllWindows()
cap.release()
proc1.terminate()

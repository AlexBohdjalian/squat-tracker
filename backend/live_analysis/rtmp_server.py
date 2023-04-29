import logging
import socket
import subprocess
import time
from threading import Thread

import cv2
import squat_analyser as sa
from flask import Flask, jsonify


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
    '-r', '10',  # Set the output frame rate to 10 FPS
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


# Begin re-streaming to a local endpoint
proc1 = subprocess.Popen(
    ffmpeg_args,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT
)
time.sleep(3) # Allow server to start before opening rtmp stream


# start_string = 'Input #0, flv, from '
# print('Waiting for client to connect...')
# while True:
#     output = proc1.stdout.readline().decode('utf-8').strip()
#     if start_string in output:
#         print('Connection request received...')
#         break

cap.open(local_rtmp_endpoint)
print('Stream started!')

show_stream = False
show_feedback = True
try:
    while True:
        # Process the frame
        immediate_f, success = form_analyser.analyse(cap, show_output=show_stream)
        if not success:
            break

        if show_feedback and immediate_f not in [[], current_f]:
            for f in immediate_f:
                if f['tag'] in ['FEEDBACK']:
                    print(f'{f["tag"]}: {f["message"]}')
                elif f['tag'] == 'REP_DETECTED':
                    print('Rep detected')
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

print('Server successfully shutdown!')

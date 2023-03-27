import subprocess
import cv2
import socket
import requests
from squat_analysis_be_v2 import process_live_video_from_fe

ip = socket.gethostbyname(socket.gethostname())
video_stream_input = f'rtmp://{ip}:1935/form_analyser/22022001'
local_rtmp_endpoint = 'rtmp://localhost:1935/live/app'

# Receives a stream from the host and forwards it to a local RTMP endpoint
ffmpeg_cmd = f'ffmpeg -f flv -listen 1 -i {video_stream_input} -c copy -f flv {local_rtmp_endpoint}'
# ffmpeg_cmd = f'ffmpeg -re -i {video_stream_input} -f flv {local_rtmp_endpoint}'

cap = cv2.VideoCapture()
proc1 = subprocess.Popen(ffmpeg_cmd) # shell=True ?
cap.open(local_rtmp_endpoint)

if not cap.isOpened():
    print('Stream not open')
    proc1.kill()
    exit()

while True:
    # SET MODEL COMPLEXITY TO 0
    # immediate_form_feedback, suc = process_live_video_from_fe(
    #     cap,
    #     show_output=True
    # )
    suc, frame = cap.read()
    if not suc:
        break
    cv2.imshow('frame', frame)
    cv2.waitKey(1)

    # send immediate form feedback back to app via post request at ip on port 5000
    # requests.post(
    #     f'http://{ip}:5000',
    #     json={"feedback": immediate_form_feedback}
    # )

# SEND SUMMARY HERE?
# e.f. requests.post(...)
cv2.destroyAllWindows()
cap.release()
proc1.kill()

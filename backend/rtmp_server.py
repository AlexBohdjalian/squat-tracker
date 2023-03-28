import subprocess
import cv2
import socket
from squat_analysis_be_v2 import process_live_video_from_fe


# Declare constants for server and commands
port = 8080
ip = socket.gethostbyname(socket.gethostname())
video_stream_input = f'rtmp://{ip}:1935/form_analyser/22022001'
local_rtmp_endpoint = 'rtmp://localhost/live'
ffmpeg_args = ['ffmpeg', '-re', '-f', 'flv', '-listen', '1', '-i', video_stream_input, '-copyts', '-fps_mode', '1', '-c', 'copy', '-f', 'flv', '-listen', '1', local_rtmp_endpoint]

# Begin forwarding rtmp stream to a local endpoint
proc1 = subprocess.Popen(ffmpeg_args)

# Read the local rtmp stream
cap = cv2.VideoCapture()
cap.open(local_rtmp_endpoint)

if not cap.isOpened():
    print('Stream not open')
    proc1.kill()
    exit()

while True:
    # Process the frame
    immediate_form_feedback, suc = process_live_video_from_fe(
        cap,
        show_output=True
    )
    if not suc:
        break
    
    print(immediate_form_feedback)

    # Send the feedback back to the client
    # TODO: Send feedback here somehow

cv2.destroyAllWindows()
cap.release()
proc1.kill()

# Do then send a final summary of workout?
# Or make it simultaneously record video for post-processing?

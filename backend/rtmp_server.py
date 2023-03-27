import subprocess
import cv2
import socket


# ip = socket.gethostbyname(socket.gethostname())
# video_stream_input = f'rtmp://{ip}:1935/form_analyser/22022001'
local_rtmp_endpoint = 'rtmp://localhost/live'

# THIS COMMAND WORKS!!!!!!!!
# ffmpeg -re -f flv -listen 1 -i rtmp://192.168.0.28:1935/form_analyser/22022001 -c copy -f flv -listen 1 rtmp://localhost/live

# This command works to save the video:
# ffmpeg -re -f flv -listen 1 -i rtmp://192.168.0.28:1935/form_analyser/22022001 -c copy -f flv output.flv

# ffmpeg_cmd = f'ffmpeg -re -f flv -listen 1 -i {video_stream_input} -c copy -f flv {local_rtmp_endpoint}'
# proc1 = subprocess.Popen(ffmpeg_cmd, shell=True)

cap = cv2.VideoCapture(local_rtmp_endpoint)
# cap.open(local_rtmp_endpoint)

if not cap.isOpened():
    print('Stream not open')
    # proc1.kill()
    exit()

while True:
    suc, frame = cap.read()
    if not suc:
        break
    cv2.imshow('Stream', frame)
    cv2.waitKey(1)

cv2.destroyAllWindows()
cap.release()
# proc1.kill()



# # TODO: implement pose estimation using a macbook app and compare the stats
#     # explaining why this approach is limited but necessary

# while True:
#     # SET MODEL COMPLEXITY TO 0
#     # immediate_form_feedback, suc = process_live_video_from_fe(
#     #     cap,
#     #     show_output=True
#     # )
#     suc, frame = cap.read()
#     if not suc:
#         break
#     cv2.imshow('frame', frame)
#     cv2.waitKey(1)

#     # send immediate form feedback back to app via post request at ip on port 5000
#     # requests.post(
#     #     f'http://{ip}:5000',
#     #     json={"feedback": immediate_form_feedback}
#     # )

# # SEND SUMMARY HERE?
# # e.f. requests.post(...)
# cv2.destroyAllWindows()
# cap.release()
# proc1.kill()

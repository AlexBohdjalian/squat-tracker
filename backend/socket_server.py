import flask
import cv2
import base64
import json
import os
import numpy as np
import time
from mediapipe_squat_analysis import process_video_from_fe



app = flask.Flask(__name__)

@app.route('/process_frame', methods=['POST'])
def process_frame():
    print('Receiving data...')
    s = time.time()
    frame_data = base64.b64decode(flask.request.json['frame'])
    print('Data received...')

    np_arr =  np.fromstring(frame_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    processed_frame = frame#some_function(frame)
    _, encoded_frame = cv2.imencode('.jpg', processed_frame)
    print(time.time() - s)

    cv2.imshow('frame', frame)
    cv2.waitKey(2000)


    return 'done'


@app.route('/process_video', methods=['POST'])
def process_video():
    # Receive the data in chunks
        # create some fe logic to determine how many frames are sent per chunk and include the count in the header
        # recieve the chunks, write to video file
        # process, send back
        # make asynchronous

    print('Receiving data...')
    video_data = flask.request.json['video']
    print('Data received...')

    file_path = os.path.abspath('tmp/video.mp4')

    with open(file_path, 'wb') as fw:
        fw.write(base64.b64decode(video_data))

    # TODO: create a new function which does everything needed (efficiently in this context), that then returns the raw data to be sent to the app
    processed_video_path, form_analysis = process_video_from_fe(file_path, frame_skip)

    with open(processed_video_path, 'rb') as fr:
        processed_video_data = fr.read()

    os.remove('tmp/video.mp4')

    return {
        'video': base64.b64encode(processed_video_data).decode('utf-8'),
        'analysis': form_analysis,
    }


if __name__ == '__main__':
    frame_skip = 3
    app.run(host='192.168.0.28', port=5000)

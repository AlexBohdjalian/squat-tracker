import flask
import cv2
import base64
import os
import numpy as np
from squat_analyser import process_video_from_fe, process_frame_from_fe


app = flask.Flask(__name__)

@app.route('/process_frame', methods=['POST'])
def process_frame():
    frame_data = base64.b64decode(flask.request.json['frame'])

    np_arr =  np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    form_feedback = process_frame_from_fe(frame)

    return form_feedback


@app.route('/process_video', methods=['POST'])
def process_video():
    # Receive the data in chunks
        # create some fe logic to determine how many frames are sent per chunk and include the count in the header
        # receive the chunks, write to video file
        # process, send back
        # make asynchronous

    print('Receiving data...')
    video_data = flask.request.json['video']
    print('Data received...')

    file_path = os.path.abspath('tmp/video.mp4')

    with open(file_path, 'wb') as fw:
        fw.write(base64.b64decode(video_data))

    # TODO: create a new function which does everything needed (efficiently in this context), that then returns the raw data to be sent to the app
    processed_video_path, form_analysis = process_video_from_fe(file_path)

    with open(processed_video_path, 'rb') as fr:
        processed_video_data = fr.read()

    os.remove(file_path)
    os.remove(processed_video_path)

    return {
        'video': base64.b64encode(processed_video_data).decode('utf-8'),
        'analysis': form_analysis,
    }


if __name__ == '__main__':
    frame_skip = 3
    # TODO: implement threading for multiple client connections (if flask doesn't already do that)
    app.run(host='192.168.0.28', port=5000)
    

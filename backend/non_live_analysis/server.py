import base64
import os
import socket
import tempfile

from flask import Flask, jsonify, request
from squat_analyser import SquatFormAnalyser

app = Flask(__name__)

form_analyser = SquatFormAnalyser(model_complexity=2)

@app.route('/upload_video', methods=['POST'])
def upload_video():
    print('Receiving video from client...')
    video_base64 = request.get_data()  # Get the base64 video data from the request
    if not video_base64:
        return 'No video file found', 400
    print('Processing video from client...')

    # Save the uploaded video to a temporary file
    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video_data = base64.b64decode(video_base64)
    with open(temp_video_file.name, 'wb') as f:
        f.write(video_data)

    # Process the video file using MediaPipeDetector (or any other processing)
    temp_proc_file, final_summary = form_analyser.analyse(temp_video_file.name)
    temp_video_file.close()
    os.unlink(temp_video_file.name)

    # Encode the processed video
    with open(temp_proc_file.name, 'rb') as videoFile:
        base64Video = base64.b64encode(videoFile.read()).decode('utf-8')

    temp_proc_file.close()
    os.unlink(temp_proc_file.name)

    print('Done.')
    return jsonify({"processed_video": base64Video, "final_summary": final_summary})


if __name__ == '__main__':
    ip = socket.gethostbyname(socket.gethostname())
    app.run(host=ip, port=5000, threaded=True)

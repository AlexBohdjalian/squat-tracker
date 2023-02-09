from flask import Flask, request
import cv2
import numpy as np
from backend.mediapipe_estimator import MediaPipeDetector
from backend.squat_check import SquatFormAnalyzer
import pickle


app = Flask(__name__)

def some_function(frame):
    # Process the frame
    landmarks = pose_estimator.make_prediction(frame)
    landmark_list = form_analyser.get_landmarks(landmarks)

    squat_details = form_analyser.determine_squat_stage(landmark_list) # For now just get 'Standing'|'Bottom' and angles
    
    return

@app.route('/process_frame', methods=['POST'])
def process_frame():
    # Receive and decode the camera frame
    frame = request.data
    frame = np.frombuffer(frame, dtype=np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    
    # Process and return the data
    landmarks = pose_estimator.make_prediction(frame)
    squat_details = form_analyser.determine_squat_stage(landmarks) # For now just get 'Standing'|'Bottom' and angles

    response = pickle.dumps([landmarks, squat_details])
    
    return response, 200

if __name__ == '__main__':
    pose_estimator = MediaPipeDetector()
    form_analyser = SquatFormAnalyzer()
    app.run(host='0.0.0.0', port=5000, debug=True)

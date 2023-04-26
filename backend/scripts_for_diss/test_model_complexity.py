import timeit

import cv2
import mediapipe as mp
from mediapipe_estimator import MediaPipeDetector


image = cv2.imread('./assets/mediapipe_model_complexity_frame.jpg')
number = 1000

for model_complexity in [0, 1, 2]:
    classifier = MediaPipeDetector(model_complexity=model_complexity)

    # Timing 
    time = timeit.timeit(lambda: classifier.make_prediction(image), number=number)
    print(f'Model Complexity: {model_complexity}, time: {round(time/number, 3)}')

    # Visualise
    pose_landmarks = classifier.make_prediction(image)
    frame = image.copy()
    mp.solutions.drawing_utils.draw_landmarks(
        frame,
        pose_landmarks,
        mp.solutions.pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style()
    )
    cv2.imshow(f'Model Complexity: {model_complexity}', frame)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()

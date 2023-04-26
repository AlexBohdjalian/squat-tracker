from mediapipe_estimator import MediaPipeDetector
import cv2
import mediapipe as mp

image = cv2.imread('./assets/goblet_squat_frame.jpg')
classifier = MediaPipeDetector(model_complexity=2)
landmarks = classifier.make_prediction(image)
mp.solutions.drawing_utils.draw_landmarks(
    image,
    landmarks,
    mp.solutions.pose.POSE_CONNECTIONS,
    landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style()
)
cv2.imwrite('./assets/processed/landmark_overlay.png', image)

image = cv2.imread('./assets/mediapipe_model_complexity_frame.jpg')
classifier = MediaPipeDetector(model_complexity=0)
landmarks = classifier.make_prediction(image)
mp.solutions.drawing_utils.draw_landmarks(
    image,
    landmarks,
    mp.solutions.pose.POSE_CONNECTIONS,
    landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style()
)
cv2.imwrite('./assets/processed/bad_landmark_overlay.png', image)

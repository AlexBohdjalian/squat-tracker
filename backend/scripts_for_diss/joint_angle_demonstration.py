from mediapipe_estimator import MediaPipeDetector
import mediapipe as mp
import cv2
import numpy as np
import os

classifier = MediaPipeDetector(model_complexity=2)

landmark_names = {
    'nose': 0,
    'left_eye_inner': 1,
    'left_eye': 2,
    'left_eye_outer': 3,
    'right_eye_inner': 4,
    'right_eye': 5,
    'right_eye_outer': 6,
    'left_ear': 7,
    'right_ear': 8,
    'mouth_left': 9,
    'mouth_right': 10,
    'left_shoulder': 11,
    'right_shoulder': 12,
    'left_elbow': 13,
    'right_elbow': 14,
    'left_wrist': 15,
    'right_wrist': 16,
    'left_pinky': 17,
    'right_pinky': 18,
    'left_index': 19,
    'right_index': 20,
    'left_thumb': 21,
    'right_thumb': 22,
    'left_hip': 23,
    'right_hip': 24,
    'left_knee': 25,
    'right_knee': 26,
    'left_ankle': 27,
    'right_ankle': 28,
    'left_heel': 29,
    'right_heel': 30,
    'left_foot_index': 31,
    'right_foot_index': 32
}

def draw_text(img, text,
    to_centre=False,
    font=cv2.FONT_HERSHEY_PLAIN,
    pos=(0, 0),
    font_scale=3,
    font_thickness=2,
    text_color=(219, 123, 3),
    text_color_bg=(0, 0, 0)
):
    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    if to_centre:
        x -= text_w // 2
        y -= text_h // 2
    cv2.rectangle(img, (x, y), (x + text_w, y + text_h), text_color_bg, -1)
    cv2.putText(
        img,
        text,
        (x, y + text_h + font_scale - 1),
        font,
        font_scale,
        text_color,
        font_thickness
    )

    return text_size

def calc_3D_angle(joint1, joint2, joint3):
    # Create vectors from joint2 to joint1 and joint2 to joint3
    vector1 = np.array([joint1.x - joint2.x, joint1.y - joint2.y, joint1.z - joint2.z])
    vector2 = np.array([joint3.x - joint2.x, joint3.y - joint2.y, joint3.z - joint2.z])

    # Calculate the dot product and magnitudes of the vectors
    dot_product = np.dot(vector1, vector2)
    magnitude1_squared = np.dot(vector1, vector1)
    magnitude2_squared = np.dot(vector2, vector2)

    # Calculate the angle between the vectors in radians
    radians = np.arccos(dot_product / np.sqrt(magnitude1_squared * magnitude2_squared))

    # Convert radians to degrees
    angle = np.rad2deg(radians)

    return angle

for path in ['./assets/standing.jpg', './assets/squatting.jpg']:
    image = cv2.imread(path)
    pose_landmarks = classifier.make_prediction(image)

    mp.solutions.drawing_utils.draw_landmarks(
        image,
        pose_landmarks,
        mp.solutions.pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style()
    )

    joint_dict = {
        joint_name: pose_landmarks.landmark[landmark_names[joint_name]]
        for joint_name in landmark_names.keys()
    }

    toe, ankle, knee, hip, shoulder = [joint_dict[name]
    for name in ['left_foot_index', 'left_ankle', 'left_knee', 'left_hip', 'left_shoulder']]

    ankle_angle = round(calc_3D_angle(toe, ankle, knee), 1)
    knee_angle = round(calc_3D_angle(ankle, knee, shoulder), 1)
    hip_angle = round(calc_3D_angle(knee, hip, shoulder), 1)

    ankle_pos = tuple(np.multiply([ankle.x, ankle.y], image.shape[:2][::-1]).astype(int))
    knee_pos = tuple(np.multiply([knee.x, knee.y], image.shape[:2][::-1]).astype(int))
    hip_pos = tuple(np.multiply([hip.x, hip.y], image.shape[:2][::-1]).astype(int))

    draw_text(image, str(ankle_angle) + ' deg', True, pos=ankle_pos, font_thickness=3)
    draw_text(image, str(knee_angle) + ' deg', True, pos=knee_pos, font_thickness=3)
    draw_text(image, str(hip_angle) + ' deg', True, pos=hip_pos, font_thickness=3)

    cv2.imwrite('./assets/processed/' + os.path.basename(path)[:-4] + '_joint_angle_example.png', image)


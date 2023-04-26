from mediapipe_estimator import MediaPipeDetector
import mediapipe as mp
import cv2

image = cv2.imread('./assets/vertically_misaligned_example.jpg')
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

pose_landmarks = classifier.make_prediction(image)

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

def check_joints_are_vertically_aligned(left_joint1, right_joint1, left_joint2, right_joint2, threshold):
    joint1_mid = abs(right_joint1.x + abs(right_joint1.x - left_joint1.x) / 2)
    joint2_mid = abs(right_joint2.x + abs(right_joint2.x - left_joint2.x) / 2)
    return abs(joint1_mid - joint2_mid) <= threshold

hip_vertically_aligned_threshold = 0.04
shoulder_vertically_aligned_threshold = 0.075

mp.solutions.drawing_utils.draw_landmarks(
    image,
    pose_landmarks,
    mp.solutions.pose.POSE_CONNECTIONS,
    landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style()
)

left_shoulder, right_shoulder, left_hip, right_hip, left_ankle, right_ankle = [pose_landmarks.landmark[landmark_names[joint_name]]
for joint_name in ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip', 'left_ankle', 'right_ankle']]

check_hips = check_joints_are_vertically_aligned(left_hip, right_hip, left_ankle, right_ankle, hip_vertically_aligned_threshold)
check_shoulders = check_joints_are_vertically_aligned(left_shoulder, right_shoulder, left_ankle, right_ankle, shoulder_vertically_aligned_threshold)

draw_text(image, 'Vertical Alignment', font_thickness=3)
draw_text(image, 'Hips: ' + str(check_hips), pos=(0, 35), font_thickness=3)
draw_text(image, 'Shoulders: ' + str(check_shoulders), pos=(0, 70), font_thickness=3)

cv2.imwrite('./assets/processed/vertical_alignment_example.png', image)
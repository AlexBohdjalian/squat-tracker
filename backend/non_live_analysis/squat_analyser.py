import cv2
import numpy as np
from mediapipe_estimator import MediaPipeDetector
from form_analyser import MediaPipe_To_Form_Interpreter
import tempfile
import mediapipe as mp

class SquatFormAnalyser():
    def __init__(self, model_complexity, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        self.pose_estimator = MediaPipeDetector(model_complexity=model_complexity)
        self.form_analyser = MediaPipe_To_Form_Interpreter(confidence_threshold=confidence_threshold)
        self.threshold = {
            'hips_vertically_aligned': 0.05,
            'shoulders_vertically_aligned': 0.05,
        }

    def analyse(self, video_path, show_output=False):
        cap = cv2.VideoCapture(video_path)

        temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(
            temp_video_file.name,
            cv2.VideoWriter_fourcc(*'mp4v'),
            cap.get(cv2.CAP_PROP_FPS),
            (width, height)
        )

        final_summary = {}
        while True:
            success, frame = cap.read()
            if not success:
                break

            # Get landmarks
            pose_landmarks = self.pose_estimator.make_prediction(frame)

            if pose_landmarks is not None:
                # Draw landmarks
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    pose_landmarks,
                    mp.solutions.pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style()
                )

                # Get joint dictionaries
                joints_dict = self.form_analyser.get_joints_dict(pose_landmarks)
                most_visible_side = self.form_analyser.get_most_visible_side(joints_dict)
                most_visible_joints_dict = {
                    joint_name: joints_dict[most_visible_side + joint_name]
                    for joint_name in self.form_analyser.main_joints
                }
                mv_toe, mv_ankle, mv_knee, mv_hip, mv_shoulder, mv_elbow = [most_visible_joints_dict[joint] for joint in ['foot_index', 'ankle', 'knee', 'hip', 'shoulder', 'elbow']]

                # Calculate important angles
                mv_ankle_angle = self.__get_angle_if_confident([mv_toe, mv_ankle, mv_knee])
                mv_hip_angle = self.__get_angle_if_confident([mv_ankle, mv_knee, mv_hip])
                mv_knee_angle = self.__get_angle_if_confident([mv_knee, mv_hip, mv_shoulder])
                mv_shoulder_angle = self.__get_angle_if_confident([mv_hip, mv_shoulder, mv_elbow])

                # Draw joint angles
                for joint, joint_angle in [
                    (mv_ankle, mv_ankle_angle),
                    (mv_knee, mv_hip_angle),
                    (mv_hip, mv_knee_angle),
                    (mv_shoulder, mv_shoulder_angle)
                ]:
                    if joint_angle is not None:
                        self.__draw_angle_at_joint(frame, joint, joint_angle)

                # Draw line verticals
                left_ankle, right_ankle = joints_dict['left_ankle'], joints_dict['right_ankle']
                if self.form_analyser.check_confidence(self.confidence_threshold, [left_ankle, right_ankle]):
                    ankle_mid_point_x = (left_ankle.x + right_ankle.x) / 2
                    print(ankle_mid_point_x * frame.shape[1])
                    self.__draw_vertical_at_point(frame, int(ankle_mid_point_x * frame.shape[1]), (255, 0, 0))

                    for left_joint, right_joint, threshold in [[joints_dict['left_' + j], joints_dict['right_' + j], th] for j, th in [
                        ('shoulder', self.threshold['shoulders_vertically_aligned']),
                        ('hip', self.threshold['hips_vertically_aligned'])
                    ]]:
                        if self.form_analyser.check_confidence(self.confidence_threshold, [left_joint, right_joint]):
                            mid_point_x = (left_joint.x + right_joint.x) / 2
                            colour = (0, 255, 0) if abs(ankle_mid_point_x - mid_point_x) < threshold else (0, 0, 255)
                            self.__draw_vertical_at_point(frame, int(mid_point_x * frame.shape[1]), colour)

                # TODO: form analysis...

            if show_output:
                cv2.imshow('Video', frame)
                cv2.waitKey(1)

            out.write(frame)

        cv2.destroyAllWindows()
        cap.release()
        out.release()

        # TODO: Create final summary (test data for now)
        final_summary = {
            'goodReps': 1,
            'badReps': 3,
            'mistakesMade': [
                {'rep': 1, 'mistakes': []},
                {'rep': 2, 'mistakes': ['Hips went out of alignment with feet', 'Shoulders went out of alignment with feet']},
                {'rep': 3, 'mistakes': ['Hips went out of alignment with feet']},
                {'rep': 4, 'mistakes': ['Hips went out of alignment with feet', 'Shoulders were not level', 'Shoulders went out of alignment with feet']},
            ],
            'stateSequences': [
                {'durations': [1.066868543624878, 0.1766049861907959], 'states': ['STANDING', 'TRANSITION', 'BOTTOM', 'TRANSITION']},
                {'durations': [0.8746097087860107, 0.2374439239501953], 'states': ['STANDING', 'TRANSITION', 'BOTTOM', 'TRANSITION']},
                {'durations': [0.9108970165252686, 0.3012425899505615], 'states': ['STANDING', 'TRANSITION']},
                {'durations': [1.1003923004023002, 0.2652425899505615], 'states': ['STANDING', 'TRANSITION', 'BOTTOM', 'TRANSITION']},
            ],
            'finalComments': 'NOT IMPLEMENTED YET'
        }

        return temp_video_file, final_summary

    def __get_angle_if_confident(self, angles):
        if self.form_analyser.check_confidence(self.confidence_threshold, angles):
            return self.form_analyser.calc_3D_angle(*angles)

        return None

    def __draw_vertical_at_point(self, frame, x_pos, colour):
        cv2.line(frame, (x_pos, 0), (x_pos, frame.shape[0]), colour, thickness=3)

    def __draw_angle_at_joint(self, frame, joint, joint_angle):
        joint_pos = tuple(np.multiply([joint.x, joint.y], frame.shape[:2][::-1]).astype(int))
        self.__draw_text(
            frame,
            f'{round(joint_angle)} deg',
            to_centre=True,
            pos=joint_pos
        )

    def __draw_text(self, img, text,
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

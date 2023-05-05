import cv2
import numpy as np
from mediapipe_estimator import MediaPipeDetector
from form_analyser import MediaPipe_To_Form_Interpreter
import tempfile
import mediapipe as mp

class SquatFormAnalyser():
    def __init__(self, model_complexity, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_spec = mp.solutions.drawing_styles.get_default_pose_landmarks_style()
        self.pose_estimator = MediaPipeDetector(model_complexity=model_complexity)
        self.form_analyser = MediaPipe_To_Form_Interpreter(confidence_threshold=confidence_threshold)
        self.threshold = {
            'hips_vertically_aligned': 0.05,
            'shoulders_vertically_aligned': 0.05,
            'shoulders_level': 0.05
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

            message_to_display = []
            if pose_landmarks is not None:
                # Draw landmarks
                self.mp_draw.draw_landmarks(
                    frame,
                    pose_landmarks,
                    mp.solutions.pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_spec
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

                # Draw vertical alignment indicators if out of alignment
                left_ankle, right_ankle = joints_dict['left_ankle'], joints_dict['right_ankle']
                if self.form_analyser.check_confidence(self.confidence_threshold, [left_ankle, right_ankle]):
                    ankle_mid_point = ((left_ankle.x + right_ankle.x) / 2, (left_ankle.y + right_ankle.y) / 2)
                    self.__draw_vertical_at_point(frame, np.multiply(ankle_mid_point, frame.shape[:2][::-1]).astype(int), (255, 0, 0))

                    for left_joint, right_joint, threshold, joint_name in [[joints_dict['left_' + j], joints_dict['right_' + j], th, j] for j, th in [
                        ('shoulder', self.threshold['shoulders_vertically_aligned']),
                        ('hip', self.threshold['hips_vertically_aligned'])
                    ]]:
                        if self.form_analyser.check_confidence(self.confidence_threshold, [left_joint, right_joint]):
                            mid_point = ((left_joint.x + right_joint.x) / 2, (left_joint.y + right_joint.y) / 2)
                            if abs(ankle_mid_point[0] - mid_point[0]) < threshold:
                                colour = (0, 255, 0)
                            else:
                                colour = (0, 0, 255)
                                message_to_display.append(f'{joint_name.capitalize()}s are not vertically aligned')

                            self.__draw_vertical_at_point(frame, np.multiply(mid_point, frame.shape[:2][::-1]).astype(int), colour)

                # Draw levelness indicators if not level
                left_shoulder, right_shoulder = joints_dict['left_shoulder'], joints_dict['right_shoulder']
                if self.form_analyser.check_confidence(self.confidence_threshold, [left_shoulder, right_shoulder]):
                    joints_are_level = self.form_analyser.check_joints_are_level(left_shoulder, right_shoulder, self.threshold['shoulders_level'])
                    if joints_are_level:
                        colour = (0, 255, 0)
                    else:
                        colour = (0, 0, 255)
                        message_to_display.append('Shoulders are not level')

                    colour = (0, 255, 0) if joints_are_level else (0, 0, 255)
                    self.__draw_levelness_line_at_points(frame, left_shoulder, right_shoulder, colour)


                # TODO: form analysis...
            else:
                message_to_display.append('User not detected')

            for i, msg in enumerate(message_to_display):
                self.__draw_text(frame, str(msg), pos=(0, (i+1)*35))

            if show_output:
                cv2.imshow('Video', frame)
                if cv2.waitKey(1) == ord('q'):
                    break

            out.write(frame)

        cv2.destroyAllWindows()
        cap.release()
        out.release()

        # TODO: Create final summary (test data for now)
        final_summary = {
            'goodReps': 0,
            'badReps': 0,
            'mistakesMade': [],
            'stateSequences': [],
            'finalComments': 'NOT IMPLEMENTED'
        }

        return temp_video_file, final_summary

    def __get_angle_if_confident(self, angles):
        if self.form_analyser.check_confidence(self.confidence_threshold, angles):
            return self.form_analyser.calc_3D_angle(*angles)

        return None

    def __draw_levelness_line_at_points(self, frame, left_shoulder, right_shoulder, colour):
        p1 = self.__get_image_coords_from_joint(frame.shape, left_shoulder)
        p2 = self.__get_image_coords_from_joint(frame.shape, right_shoulder)
        cv2.line(frame, p1, p2, colour, thickness=3)

    def __draw_vertical_at_point(self, frame, pos, colour):
        cv2.line(frame, (pos[0], 0), (pos[0], pos[1]), colour, thickness=3)

    def __draw_angle_at_joint(self, frame, joint, joint_angle):
        joint_pos = self.__get_image_coords_from_joint(frame.shape, joint)
        self.__draw_text(
            frame,
            f'{round(joint_angle)} deg',
            to_centre=True,
            pos=joint_pos
        )

    def __get_image_coords_from_joint(self, frame_shape, joint):
        return tuple(np.multiply([joint.x, joint.y], frame_shape[:2][::-1]).astype(int))

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

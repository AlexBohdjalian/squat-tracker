import cv2
import time
import mediapipe as mp
# from imutils.video import FileVideoStream
from mediapipe_estimator import MediaPipeDetector
from squat_form_analyser import MediaPipe_To_Form_Interpreter

STANDING = 'STANDING'
TRANSITION = 'TRANSITION'
BOTTOM = 'BOTTOM'

NORMAL = '\u001b[0m'
YELLOW = '\u001b[43m'

class SquatFormAnalyser():
    def __init__(self):
        self.pose_detector = MediaPipeDetector()
        self.form_analyser = MediaPipe_To_Form_Interpreter()
        self.frame_stack = 2
        self.frame_skip = 3
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose
        self.text_colour = (219, 123, 3)
        self.bad_form_colour = (0, 0, 255)
        self.form_thresholds_beginner = {
            'ankle': 45, # currently unused
            'knee': (50, 70, 95), 
            'hip': (10, 50)
        }
        self.form_thresholds_advanced = {
            'ankle': 30, # currently unused
            'knee': (50, 80, 115), 
            'hip': (15, 50),
            'shoulder_level': 0.05,
            'hip_level': 0.05,
        }
        self.form_thresholds = self.form_thresholds_advanced
        self.reps = []
        self.state_sequence = [STANDING]
        self.most_visible_side = ''
        self.squat_duration = 0
        self.squat_start_time = 0
        self.squat_mid_time = 0
        self.squat_end_time = 0

    def analyse(self, cap, show_output=False):
        # TODO: check cap is valid? (uncomment below)
        # if isinstance(cap, str) and cap != '0':
        #     raise ValueError('Invalid video source')

        suc, frame = cap.read()
        if not suc:
            return 'Video End', suc

        # TODO: check if squat has started with separate function
            # if it has then do estimation as below

        feedback, pose_landmarks = self.get_feedback_from_frame(frame)

        if show_output:
            # NOTE: this slows down performance
            self.mp_drawing.draw_landmarks(
                frame,
                pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            frame = cv2.resize(frame, (360, 640))
            for i in range(len(feedback)):
                self.draw_text(frame, feedback[i], pos=(0, i*35), font_scale=2)
            cv2.imshow('Live Stream', frame)
            cv2.waitKey(1)

        return feedback, suc


    def get_feedback_from_frame(self, frame):
        s = time.time()
        pose_landmarks = self.pose_detector.make_prediction(frame)
        if pose_landmarks is None:
            return ['Not Detected'], pose_landmarks

        if self.most_visible_side == '':
            self.most_visible_side = self.form_analyser.get_most_visible_side(pose_landmarks)
            if self.most_visible_side == '':
                return ['Insufficient Joint Data'], pose_landmarks

        # TODO: Determine angle of person to screen. e.g. face on or side on (allow in between?)
            # Then, adjust form criteria. E.g. if face on then check shoulders are level

        orientation = self.form_analyser.get_orientation(pose_landmarks)

        ankle_vertical_angle, knee_vertical_angle, hip_vertical_angle = self.form_analyser.get_main_joint_vertical_angles(pose_landmarks, self.most_visible_side)
        if knee_vertical_angle is not None:
            if self.state_sequence != [STANDING] and knee_vertical_angle <= 32:
                if self.state_sequence[-1] == TRANSITION:
                    squat_end_time = time.time()
                elif self.state_sequence[-1] == BOTTOM:
                    print(YELLOW, 'ANALYSIS INFO: Transition not detected. Was standing now bottom.', NORMAL)

                self.squat_duration = self.squat_end_time - self.squat_start_time
                self.reps.append([
                    [
                        self.squat_mid_time - self.squat_start_time,
                        self.squat_end_time - self.squat_mid_time
                    ],
                    self.state_sequence
                ])

                self.state_sequence = [STANDING]
            elif self.state_sequence[-1] != TRANSITION and 35 <= knee_vertical_angle <= 65:
                if self.state_sequence[-1] == STANDING:
                    self.squat_start_time = time.time()
                elif self.state_sequence[-1] == BOTTOM:
                    self.squat_mid_time = time.time()
                if self.state_sequence[-1] != TRANSITION:
                    self.state_sequence.append(TRANSITION)
            elif self.state_sequence[-1] != BOTTOM and 75 <= knee_vertical_angle <= 95:
                if self.state_sequence[-1] == STANDING:
                    print(YELLOW, 'ANALYSIS INFO: Transition not detected. Was bottom now standing.', NORMAL)
                if self.state_sequence[-1] != BOTTOM:
                    self.state_sequence.append(BOTTOM)

        # Determine Feedback (This section needs a lot of work)
        current_form_text = []
        if hip_vertical_angle is not None:
            hip_vertical_angle = round(hip_vertical_angle)
            if hip_vertical_angle > self.form_thresholds['hip'][1]:
                current_form_text.append('Bend Backwards')
            # TODO: fix this
            # elif hip_vertical_angle > self.form_thresholds['hip'][0]:
            #     current_form_text.append('Bend Forward')

        if knee_vertical_angle is not None:
            knee_vertical_angle = round(knee_vertical_angle)
            if self.form_thresholds['knee'][0] < knee_vertical_angle < self.form_thresholds['knee'][1] and \
                self.state_sequence.count('s2') == 1:
                self.current_form_text.append('Lower Hips')
            elif knee_vertical_angle > self.form_thresholds['knee'][2]:
                # 'Deep Squat'
                limit = self.form_thresholds['knee'][2]
                current_form_text.append(f'Incorrect Posture. Knee angle is: {round(knee_vertical_angle)} and should be less than {limit}')

        # Determine if hips/shoulders are level
        if orientation == 'face_on':
            if not self.form_analyser.check_joints_are_level(
                pose_landmarks,
                'shoulder',
                self.form_thresholds['shoulder_level']
            ):
                current_form_text.append(f'Shoulders are not level')
            if not self.form_analyser.check_joints_are_level(
                pose_landmarks,
                'hip',
                self.form_thresholds['hip_level']
            ):
                current_form_text.append(f'Hips are not level')

        if self.squat_end_time < self.squat_start_time:
            self.squat_duration = round(time.time() - self.squat_start_time, 2)

        return current_form_text, pose_landmarks

    def draw_text(self, img, text,
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
        cv2.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness)

        return text_size

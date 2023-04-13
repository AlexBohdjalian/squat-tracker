import time

import cv2
import mediapipe as mp
from mediapipe_estimator import MediaPipeDetector
from squat_form_analyser import MediaPipe_To_Form_Interpreter


STANDING = 'STANDING'
TRANSITION = 'TRANSITION'
BOTTOM = 'BOTTOM'

NORMAL = '\u001b[0m'
YELLOW_BG = '\u001b[43m'
RED_BG = '\u001b[41m'


# NOTES:
# TODO: see https://github.com/Pradnya1208/Squats-angle-detection-using-OpenCV-and-mediapipe_v1/blob/main/Squat%20pose%20estimation.ipynb
    # for other calculations (also below)
# TODO: below
# Range of motion
# Partial squat (0-40 degrees knee angle)
# Parallel squat (hips parallel to knees or 70-100 degrees knee angle)
# Deep squat (full range or >100 degrees knee angle)

# ref: https://www.raynersmale.com/blog/2014/1/31/optimising-your-squat
# TODO: Toque calculation: https://squatuniversity.com/2016/04/20/the-real-science-of-the-squat/
# TODO: angles: Trunk angle, Shank angle Thigh segment angle Ankle segment angle ref: https://www.quinticsports.com/squatting_technique/


class SquatFormAnalyser():
    def __init__(self, use_advanced_criteria=False):
        self.pose_detector = MediaPipeDetector()
        self.form_analyser = MediaPipe_To_Form_Interpreter()
        self.frame_stack = 2
        self.frame_skip = 3
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles.get_default_pose_landmarks_style()
        self.mp_pose = mp.solutions.pose
        self.text_colour = (219, 123, 3)
        self.bad_form_colour = (0, 0, 255)
        self.general_thresholds = {
            'set_start_stationary': 0.07,  # TODO: tune this
            'set_end_stationary': 0.15,  # TODO: tune this
            'face_on': 0.1,

            'starting_knee_angle_range': (65, 180),  # TODO: Tune this
            'starting_hip_angle_range': (75, 180),  # TODO: Tune this

            'shoulder_level': 0.05,
            'ankle_level': 0.05,  # TODO: test
            'knee_level': 0.05,  # TODO: test
            'hip_level': 0.05,  # TODO: test
        }
        self.form_thresholds_beginner = {
            'STANDING_knee_angle_range': (62, 180),  # TODO: tune this to beginner standards
            'TRANSITION_knee_angle_range': (28, 55),  # TODO: tune this to beginner standards
            'BOTTOM_knee_angle_range': (0, 26),  # TODO: tune this to beginner standards

            # 'safe_ankle_angle': 45,  # TODO: needed?
            # 'safe_knee_angle': 95,  # TODO: needed?
            'safe_hip_angle': 0,  # TODO: do this

            'hip_vertically_aligned': 0,  # TODO: do this
            'shoulder_vertically_aligned': 0,  # TODO: do this
        }
        self.form_thresholds_advanced = {
            'STANDING_knee_angle_range': (62, 180),  # TODO: tune this
            'TRANSITION_knee_angle_range': (28, 55),  # TODO: tune this
            'BOTTOM_knee_angle_range': (0, 26),  # TODO: tune this

            # 'safe_ankle_angle': 30,  # TODO: Tune this !!!!!!!!!!!!!
            # 'safe_knee_angle': 115,  # TODO: Tune this !!!!!!!!!!!!!
            'safe_hip_angle': 62,  # TODO: Tune this !!!!!!!!!!!!!

            'hip_vertically_aligned': 0.04,  # TODO: Tune this
            'shoulder_vertically_aligned': 0.075,  # TODO: Tune this
        }
        self.form_thresholds = self.form_thresholds_advanced if use_advanced_criteria else self.form_thresholds_beginner
        self.state_sequence = [STANDING]
        self.set_has_begun = False
        self.most_visible_side = ''
        self.joint_buffer = []  # TODO: change usage of this to be clearer?
        self.joint_buffer_size = 2  # NOTE: this assumption is hard-coded elsewhere, change?
        self.stationary_duration = 3.0
        self.stationary_start_time = None
        self.set_ended_counter = 0
        self.set_ended_threshold = 5
        self.no_confident_detection_count = 0
        self.no_detection_count_threshold = 10
        self.squat_duration = 0
        self.squat_start_time = 0
        self.squat_mid_time = 0
        self.squat_end_time = 0

    def __initialise_state(self):
        self.state_sequence = [STANDING]
        self.set_has_begun = False
        self.most_visible_side = ''
        self.joint_buffer = []
        self.stationary_start_time = None
        self.set_ended_counter = 0
        self.no_confident_detection_count = 0
        self.squat_duration = 0
        self.squat_start_time = 0
        self.squat_mid_time = 0
        self.squat_end_time = 0

    def analyse(self, cap, show_output=True):
        # Get a frame
        success, frame = cap.read()
        if not success:
            return 'Video End', success

        # Get pose landmarks
        pose_landmarks = self.pose_detector.make_prediction(frame)

        # TODO: decide what types there are for feedback
            # USER_INFO - ...
            # FEEDBACK - ...
            # TIP - ...

        feedback = []

        if pose_landmarks is None:
            feedback = [('USER_INFO', 'Not Detected')]

            # TODO: if not detected, for a while, handle

        else:
            # Get dictionary of joints for ease of use
            joints_dict = self.form_analyser.get_joints_dict(pose_landmarks)

            if self.set_has_begun:
                most_visible_joints_dict = {
                    joint_name: joints_dict[self.most_visible_side + joint_name]
                    for joint_name in self.form_analyser.main_joints
                }

                if self.form_analyser.check_confidence(
                    self.form_analyser.min_confidence_threshold,
                    list(most_visible_joints_dict.values())
                ):
                    self.no_confident_detection_count = 0

                    # TODO: review how well __check_set_has_ended works
                    if self.__check_set_has_ended(most_visible_joints_dict['ankle']):
                        # TODO: return summary here?
                        feedback = [('USER_INFO', 'Set has ended')]

                        self.__initialise_state()
                        self.form_analyser.initialise_state()
                    else:
                        feedback = self.get_feedback_based_on_joints_dict(
                            joints_dict,
                            most_visible_joints_dict
                        )
                else:
                    self.no_confident_detection_count += 1
                    if self.no_confident_detection_count >= self.no_detection_count_threshold:
                        # TODO: return summary here?
                        feedback = [('USER_INFO', 'Set ended (user not detected)')]
            else:
                left_joints = [joints_dict['left_' + j] for j in self.form_analyser.main_joints]
                right_joints = [joints_dict['right_' + j] for j in self.form_analyser.main_joints]

                if self.form_analyser.check_confidence(
                    self.form_analyser.min_confidence_threshold,
                    left_joints
                ) or self.form_analyser.check_confidence(
                    self.form_analyser.min_confidence_threshold,
                    right_joints
                ):
                    if self.stationary_start_time is None:
                        time_remaining = self.stationary_duration
                    else:
                        # TODO: change this to work with frame count, not time as causes flakiness and inaccuracy
                        time_remaining = round(self.stationary_duration - time.time() + self.stationary_start_time, 2)

                    feedback = [('USER_INFO', f'Stay still for {time_remaining} seconds to start set')]

                    most_visible_side = self.form_analyser.get_most_visible_side(
                        left_joints,
                        right_joints,
                        set_begun=False
                    )
                    if self.__check_set_has_begun(joints_dict, most_visible_side):
                        self.most_visible_side = self.form_analyser.get_most_visible_side(
                            left_joints,
                            right_joints,
                            set_begun=True
                        )
                        self.set_has_begun = True
                        self.joint_buffer = []
                else:
                    feedback = [('USER_INFO', 'Insufficient joints visible')]

                    self.stationary_start_time = None
                    self.joint_buffer = []

        # NOTE: this slows down performance
        if show_output:
            self.mp_drawing.draw_landmarks(
                frame,
                pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles
            )
            frame = cv2.resize(frame, (360, 640))
            for i, (_, f) in enumerate(feedback):
                self.__draw_text(frame, str(f), pos=(0, 35 * i), font_scale=2)
            cv2.imshow('Live Stream', frame)
            cv2.waitKey(1)

        return feedback, success

    def get_feedback_based_on_joints_dict(self, joints_dict, most_visible_joints_dict):
        """ Analyses joint positions relative to current state sequence and form criteria to determine immediate feedback for user.
        Assumes that the confidence of the joints joints_dict is high enough. """
        ###### Determine orientation and angles ######
        orientation = self.form_analyser.get_orientation(
            joints_dict['left_shoulder'],
            joints_dict['right_shoulder'],
            joints_dict['left_hip'],
            joints_dict['right_hip'],
            self.general_thresholds['face_on']
        )
        knee_angle, hip_angle = self.form_analyser.get_main_joint_angles(most_visible_joints_dict)


        ##### Determine state_sequence based on angles #####
        final_feedback = []
        # TODO: change this first check to check actual desired sequence is seen
            # ['STANDING', 'TRANSITION'] is acceptable (if depth is bad) but only when timing is right?
            # or, discard non valid reps and rely on checks below to relay feedback (only count good reps)
        if self.state_sequence != [STANDING] and self.form_thresholds['STANDING_knee_angle_range'][0] <= knee_angle <= self.form_thresholds['STANDING_knee_angle_range'][1]:
            if self.state_sequence[-1] == TRANSITION:
                self.squat_end_time = time.time()
            elif self.state_sequence[-1] == BOTTOM:
                pass
                # print(f'{YELLOW_BG} ANALYSIS INFO: Transition not detected. Was standing now bottom. {NORMAL}')

            # TODO: change this to be standing_to_bottom_time, bottom_time, bottom_to_standing_time?
            # TODO: review time/duration stuff in general

            self.squat_duration = self.squat_end_time - self.squat_start_time
            s_to_m = self.squat_mid_time - self.squat_start_time
            m_to_e = self.squat_end_time - self.squat_mid_time

            final_feedback.append(('STATE_SEQUENCE', ((s_to_m, m_to_e), self.state_sequence)))
            self.state_sequence = [STANDING]
        elif self.state_sequence[-1] != TRANSITION and self.form_thresholds['TRANSITION_knee_angle_range'][0] <= knee_angle <= self.form_thresholds['TRANSITION_knee_angle_range'][1]:
            if self.state_sequence[-1] == STANDING:
                self.squat_start_time = time.time()
            elif self.state_sequence[-1] == BOTTOM:
                self.squat_mid_time = time.time()
            if self.state_sequence[-1] != TRANSITION:
                self.state_sequence.append(TRANSITION)
        elif self.state_sequence[-1] != BOTTOM and self.form_thresholds['BOTTOM_knee_angle_range'][0] <= knee_angle <= self.form_thresholds['BOTTOM_knee_angle_range'][1]:
            if self.state_sequence[-1] == STANDING:
                pass
                # print(f'{YELLOW_BG} ANALYSIS INFO: Transition not detected. Was bottom now standing. {NORMAL}')
            if self.state_sequence[-1] != BOTTOM:
                self.state_sequence.append(BOTTOM)


        ###### Determine Feedback ######
        if self.form_thresholds['TRANSITION_knee_angle_range'][0] < knee_angle < self.form_thresholds['TRANSITION_knee_angle_range'][1] and \
            self.state_sequence.count(TRANSITION) == 1:
            # TODO: redo this to identify if eccentric was complete without good depth, rather than cueing to keep going deeper
            final_feedback.append(('TIP', 'Lower Hips'))
        # elif self.form_thresholds['safe_knee_angle'] < knee_angle:
        #     # 'Deep Squat' # TODO: what is this comment?
        #     final_feedback.append(('FEEDBACK', f'Incorrect Posture. Knee angle is: {knee_angle} and should be less than {self.form_thresholds["safe_knee_angle"]}'))

        if self.state_sequence[-1] == BOTTOM:
            if not self.form_analyser.check_joints_are_level(
                joints_dict['left_knee'],
                joints_dict['right_knee'],
                self.general_thresholds['knee_level']
            ):
                final_feedback.append(('FEEDBACK', 'Knees are not level'))

        # TODO: check this and move 35 (constant) into form_thresholds
        if self.state_sequence[-1] == TRANSITION and knee_angle < 35 and self.form_thresholds['safe_hip_angle'] < hip_angle:
            # TODO: TRANSITION happens early-ish, so this check is done while close to upright. causes misread. check that knee angle is certain amount?
            final_feedback.append(('FEEDBACK', f'Bend Backwards (knee: {knee_angle}, hip: {hip_angle})'))

        # TODO: make this more robust if set stage measurement fails
        if self.squat_end_time < self.squat_start_time:
            self.squat_duration = round(time.time() - self.squat_start_time, 2)


        ##### Determine feedback specific to user camera orientation #####
        if orientation == 'face_on':
            # TODO: move this out of orientation check?
            # TODO: is this necessary?
            if not self.form_analyser.check_joints_are_level(
                joints_dict['left_ankle'],
                joints_dict['right_ankle'],
                self.general_thresholds['ankle_level']
            ):
                final_feedback.append(('FEEDBACK', 'Ankles are not level'))

            # TODO: move this out of orientation check?
            if not self.form_analyser.check_joints_are_level(
                joints_dict['left_shoulder'],
                joints_dict['right_shoulder'],
                self.general_thresholds['shoulder_level']
            ):
                final_feedback.append(('FEEDBACK', 'Shoulders are not level'))

            # TODO: move this out of orientation check?
            if not self.form_analyser.check_joints_are_level(
                joints_dict['left_hip'],
                joints_dict['right_hip'],
                self.general_thresholds['hip_level']
            ):
                final_feedback.append(('FEEDBACK', 'Hips are not level'))

            if not self.form_analyser.check_joints_are_vertically_aligned(
                joints_dict['left_hip'],
                joints_dict['right_hip'],
                joints_dict['left_ankle'],
                joints_dict['right_ankle'],
                self.form_thresholds['hip_vertically_aligned']
            ):
                final_feedback.append(('FEEDBACK', 'Hips are not vertically aligned with feet'))

            if not self.form_analyser.check_joints_are_vertically_aligned(
                joints_dict['left_shoulder'],
                joints_dict['right_shoulder'],
                joints_dict['left_ankle'],
                joints_dict['right_ankle'],
                self.form_thresholds['shoulder_vertically_aligned']
            ):
                final_feedback.append(('FEEDBACK', 'Shoulders are not vertically aligned with feet'))
        elif orientation == 'side_on':
            # TODO: this
            pass
            # exit(f'{RED_BG} side_on form feedback not implemented {NORMAL}')

        return final_feedback

    def __add_to_joint_buffer(self, joints):
        self.joint_buffer.append(joints)

        if len(self.joint_buffer) < self.joint_buffer_size:
            return False

        if len(self.joint_buffer) > self.joint_buffer_size:
            self.joint_buffer.pop(0)

        return True

    def __check_set_has_begun(self, joints_dict, most_visible_side):
        most_visible_main_joints = {
            joint_name: joints_dict[most_visible_side + joint_name]
            for joint_name in self.form_analyser.main_joints
        }

        knee_angle, hip_angle = self.form_analyser.get_main_joint_angles(most_visible_main_joints)

        if self.form_analyser.joints_in_starting_position(
            knee_angle,
            hip_angle,
            self.general_thresholds['starting_knee_angle_range'],
            self.general_thresholds['starting_hip_angle_range']
        ):
            if not self.__add_to_joint_buffer(most_visible_main_joints):
                return False

            if self.__joint_buffer_is_stationary():
                if self.stationary_start_time is None:
                    # TODO: change this to work with frame count and not time
                    self.stationary_start_time = time.time()
                elif time.time() - self.stationary_start_time > self.stationary_duration:
                    return True
            else:
                self.stationary_start_time = None
                self.joint_buffer = []
                return False
        else:
            self.stationary_start_time = None
            self.joint_buffer = []

        return False

    def __check_set_has_ended(self, most_visible_ankle):
        if not self.__add_to_joint_buffer(most_visible_ankle):
            return False

        j1 = self.joint_buffer[0]
        j2 = self.joint_buffer[1]

        distance = ((j1.x - j2.x)**2 + (j1.y - j2.y)**2 + (j1.z - j2.z)**2)**0.5
        if distance > self.general_thresholds['set_end_stationary']:
            self.set_ended_counter += 1
            if self.set_ended_counter >= self.set_ended_threshold:
                return True
        else:
            self.set_ended_counter = 0

        return False

    def __joint_buffer_is_stationary(self):
        for joint_name in self.form_analyser.main_joints:
            j1 = self.joint_buffer[0][joint_name]
            j2 = self.joint_buffer[1][joint_name]

            distance = ((j1.x - j2.x)**2 + (j1.y - j2.y)**2 + (j1.z - j2.z)**2)**0.5
            if distance > self.general_thresholds['set_start_stationary']:
                return False

        return True

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

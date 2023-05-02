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
            'set_start_stationary': 0.07,
            'set_end_stationary': 0.15,  # TODO: tune this
            'face_on': 0.12,

            'starting_knee_angle_range': (65, 180),
            'starting_hip_angle_range': (75, 180),

            'shoulder_level': 0.05,
            'knee_level': 0.05,
            'hip_level': 0.05,

            'spine_neutral': 100,  # TODO: tune this
        }
        # TODO: need to tune these values to beginner standards
        self.form_thresholds_beginner = {
            'STANDING_knee_angle_range': (62, 180),  # TODO: do this
            'TRANSITION_knee_angle_range': (28, 55),  # TODO: do this
            'BOTTOM_knee_angle_range': (0, 26),  # TODO: do this

            'safe_hip_angle': 62,  # TODO: do this

            'hip_vertically_aligned': 0.04,  # TODO: do this
            'shoulder_vertically_aligned': 0.075,  # TODO: do this
        }
        self.form_thresholds_advanced = {
            'STANDING_knee_angle_range': (62, 180),
            'TRANSITION_knee_angle_range': (28, 55),
            'BOTTOM_knee_angle_range': (0, 26),

            'safe_hip_angle': 62,

            'hip_vertically_aligned': 0.04,
            'shoulder_vertically_aligned': 0.075,
        }
        self.form_thresholds = self.form_thresholds_advanced if use_advanced_criteria else self.form_thresholds_beginner
        self.state_sequence = [STANDING]
        self.set_has_begun = False
        self.most_visible_side = ''
        self.joint_buffer = []
        self.joint_buffer_size = 2  # NOTE: this assumption is hard-coded elsewhere, change.
        self.stationary_duration = 3.0
        self.stationary_start_time = None
        self.set_ended_counter = 0
        self.set_ended_threshold = 5
        self.no_confident_detection_count = 0
        self.no_detection_count_threshold = 30
        self.no_landmarks_count = 0
        self.no_landmarks_count_threshold = 30
        self.squat_duration = 0
        self.squat_start_time = 0
        self.squat_mid_time = 0
        self.squat_end_time = 0
        self.final_summary = {
            'good_reps': 0,
            'bad_reps': 0,
            'mistakes_made': [{'rep': 1, 'mistakes': []}],
            'state_sequences': [],
            'final_comments': '',
        }
        self.current_rep_good = True


    def __initialise_state(self):
        self.state_sequence = [STANDING]
        self.set_has_begun = False
        self.most_visible_side = ''
        self.joint_buffer = []
        self.stationary_start_time = None
        self.set_ended_counter = 0
        self.no_confident_detection_count = 0
        self.no_landmarks_count = 0
        self.squat_duration = 0
        self.squat_start_time = 0
        self.squat_mid_time = 0
        self.squat_end_time = 0
        self.final_summary = {
            'good_reps': 0,
            'bad_reps': 0,
            'mistakes_made': [{'rep': 1, 'mistakes': []}], # {rep: int, mistakes: string[]}
            'state_sequences': [],
            'final_comments': '',
        }
        self.current_rep_good = True

    def analyse(self, cap, show_output=True):
        # Get a frame
        success, frame = cap.read()
        if not success:
            return 'Video Ended', success

        # Get pose landmarks
        pose_landmarks = self.pose_detector.make_prediction(frame)

        feedback = []

        if pose_landmarks is None:
            feedback = [{'tag': 'NOT_DETECTED', 'message': 'User not Detected'}]

            if self.set_has_begun:
                self.no_landmarks_count += 1
                if self.no_landmarks_count >= self.no_landmarks_count_threshold:
                    feedback = [{'tag': 'SET_ENDED', 'summary': self.__get_final_summary()}]

                    self.__initialise_state()
                    self.form_analyser.initialise_state()
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

                    if self.__check_set_has_ended(most_visible_joints_dict['ankle']):
                        feedback = [{'tag': 'SET_ENDED', 'summary': self.__get_final_summary()}]

                        self.__initialise_state()
                        self.form_analyser.initialise_state()
                    else:
                        feedback = self.get_feedback_based_on_joints_dict(
                            joints_dict,
                            most_visible_joints_dict
                        )

                        # TODO: test this fixes jittery No Detection not ending set
                        if feedback:
                            self.no_landmarks_count = 0
                else:
                    self.no_confident_detection_count += 1
                    if self.no_confident_detection_count >= self.no_detection_count_threshold:
                        feedback = [{'tag': 'SET_ENDED', 'summary': self.__get_final_summary()}]

                        self.__initialise_state()
                        self.form_analyser.initialise_state()
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
                        # TODO: change this to work with frame count, not time as causes flakiness and inaccuracy (only with test script)
                        time_remaining = round(self.stationary_duration - time.time() + self.stationary_start_time, 2)

                    feedback = [{'tag': 'SET_START_COUNTDOWN', 'message': str(time_remaining)}]

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
                        feedback = [{'tag': 'SET_STARTED', 'message': ''}]

                        self.set_has_begun = True
                        self.joint_buffer = []
                else:
                    feedback = [{'tag': 'NOT_DETECTED', 'message': 'Insufficient joints visible'}]

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
            for i, f in enumerate(feedback):
                self.__draw_text(frame, str(f), pos=(0, 35 * i), font_scale=1)
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
        if self.state_sequence[-1] != STANDING and self.form_thresholds['STANDING_knee_angle_range'][0] <= knee_angle <= self.form_thresholds['STANDING_knee_angle_range'][1]:
            if self.state_sequence[-1] == TRANSITION:
                self.squat_end_time = time.time()
            elif self.state_sequence[-1] == BOTTOM:
                pass
                # print(f'{YELLOW_BG} ANALYSIS INFO: Transition not detected. Was standing now bottom. {NORMAL}')

            # TODO: change this to be standing_to_bottom_time, bottom_time, bottom_to_standing_time

            final_feedback.append({'tag': 'REP_DETECTED', 'message': self.current_rep_good})

            self.squat_duration = self.squat_end_time - self.squat_start_time
            s_to_m = self.squat_mid_time - self.squat_start_time
            m_to_e = self.squat_end_time - self.squat_mid_time
            self.final_summary['state_sequences'].append({
                'durations': (s_to_m, m_to_e),
                'states': self.state_sequence,
            })

            self.final_summary['good_reps'] += int(self.current_rep_good)
            self.final_summary['bad_reps'] += int(not self.current_rep_good)
            current_rep = self.final_summary['mistakes_made'][-1]['rep'] + 1
            self.final_summary['mistakes_made'].append({'rep': current_rep, 'mistakes': []})
            self.current_rep_good = True

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

            self.state_sequence.append(BOTTOM)


        ###### Determine Feedback ######
        if self.form_thresholds['TRANSITION_knee_angle_range'][0] < knee_angle < self.form_thresholds['TRANSITION_knee_angle_range'][1] and \
            self.state_sequence.count(TRANSITION) == 1:
            final_feedback.append({'tag': 'TIP', 'message': 'Lower Hips'})

        if self.state_sequence[-1] == BOTTOM:
            if orientation == 'front_on' and not self.form_analyser.check_joints_are_level(
                joints_dict['left_knee'],
                joints_dict['right_knee'],
                self.general_thresholds['knee_level']
            ):
                final_feedback.append({'tag': 'FEEDBACK', 'message': 'Knees are not level'})
                self.current_rep_good = False
                self.__add_final_summary_feedback('Knees were not level')

            final_feedback.append({'tag': 'TIP', 'message': 'Keep your knees over your toes'})

        # TODO: check this and move 35 (constant) into thresholds
        if self.state_sequence[-1] == TRANSITION and knee_angle < 35 and self.form_thresholds['safe_hip_angle'] < hip_angle:
            final_feedback.append({'tag': 'FEEDBACK', 'message': f'COLLAPSED TORSO!\nKeep your spine neutral'})
            self.current_rep_good = False
            self.__add_final_summary_feedback('Torso was collapsed')

        # TODO: make this more robust if set stage measurement fails
        if self.squat_end_time < self.squat_start_time:
            self.squat_duration = round(time.time() - self.squat_start_time, 2)


        ##### Determine feedback specific to user camera orientation #####
        if orientation == 'face_on':
            if not self.form_analyser.check_joints_are_level(
                joints_dict['left_shoulder'],
                joints_dict['right_shoulder'],
                self.general_thresholds['shoulder_level']
            ):
                final_feedback.append({'tag': 'FEEDBACK', 'message': 'Shoulders are not level'})
                self.current_rep_good = False
                self.__add_final_summary_feedback('Shoulders were not level')

            if not self.form_analyser.check_joints_are_level(
                joints_dict['left_hip'],
                joints_dict['right_hip'],
                self.general_thresholds['hip_level']
            ):
                final_feedback.append({'tag': 'FEEDBACK', 'message': 'Hips are not level'})
                self.current_rep_good = False
                self.__add_final_summary_feedback('Hips were not level')

            if not self.form_analyser.check_joints_are_vertically_aligned(
                joints_dict['left_hip'],
                joints_dict['right_hip'],
                joints_dict['left_ankle'],
                joints_dict['right_ankle'],
                self.form_thresholds['hip_vertically_aligned']
            ):
                final_feedback.append({'tag': 'FEEDBACK', 'message': 'Hips are not vertically aligned with feet'})
                self.current_rep_good = False
                self.__add_final_summary_feedback('Hips went out of alignment with feet')

            if not self.form_analyser.check_joints_are_vertically_aligned(
                joints_dict['left_shoulder'],
                joints_dict['right_shoulder'],
                joints_dict['left_ankle'],
                joints_dict['right_ankle'],
                self.form_thresholds['shoulder_vertically_aligned']
            ):
                final_feedback.append({'tag': 'FEEDBACK', 'message': 'Shoulders are not vertically aligned with feet'})
                self.current_rep_good = False
                self.__add_final_summary_feedback('Shoulders went out of alignment with feet')
        elif orientation == 'side_on':
            if not self.form_analyser.check_spine_is_neutral(
                most_visible_joints_dict['hip'],
                most_visible_joints_dict['shoulder'],
                joints_dict['nose'],
                self.general_thresholds['spine_neutral']
            ):
                final_feedback.append({'tag': 'FEEDBACK', 'message': 'Maintain a neutral spine'})
                self.current_rep_good = False
                self.__add_final_summary_feedback('A neutral spine was not maintained')

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

    def __add_final_summary_feedback(self, msg):
        if msg not in self.final_summary['mistakes_made'][-1]['mistakes']:
            self.final_summary['mistakes_made'][-1]['mistakes'].append(msg)

    def __get_final_summary(self):
        if len(self.final_summary['mistakes_made']) == 0:
            self.final_summary['final_comments'] = 'Great job! No mistakes were detected during the set.'
        else:
            # TODO: this
            self.final_summary['final_comments'] = 'NOT IMPLEMENTED YET'

        return self.final_summary

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

import numpy as np
import math

class SquatFormAnalyzer():
    def __init__(self,
        confidence_threshold=0.5,
        standing_angle=175,
        standing_threshold=5,
        squatting_angle=85,
        squatting_threshold=5
    ):
        self.min_confidence_threshold = confidence_threshold
        self.standing_angle = standing_angle
        self.standing_threshold = standing_threshold
        self.squatting_angle = squatting_angle
        self.squatting_threshold = squatting_threshold
        self.landmark_names = {
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
        self.most_visible_side = ''

    def __calc_angle(self, joints):
        point1, point2, point3 = joints
        radians = np.arctan2(point3[1]-point2[1], point3[0]-point2[0]) \
                - np.arctan2(point1[1]-point2[1], point1[0]-point2[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle

    def __angle_of_singleline(self, point1, point2):
        """ Calculate angle of a single line """
        x_diff = point2[0] - point1[0]
        y_diff = point2[1] - point1[1]
        return math.degrees(math.atan2(y_diff, x_diff))

    def __dist_xy(self, point1, point2):
        """ Euclidean distance between two points point1, point2 """
        diff_point1 = (point1[0] - point2[0]) ** 2
        diff_point2 = (point1[1] - point2[1]) ** 2
        return (diff_point1 + diff_point2) ** 0.5

    def __point_position(self, point, line_pt_1, line_pt_2):
        """ Left or Right position of the point from a line """
        value = (line_pt_2[0] - line_pt_1[0]) * (point[1] - line_pt_1[1]) - \
                (line_pt_2[1] - line_pt_1[1]) * (point[0] - line_pt_1[0])
        if value >= 0:
            return "left"
        return "right"

    def __check_confidence(self, confidence_threshold, joints):
        return all(joints) and \
           all([joint[3] > confidence_threshold for joint in joints])

    def __get_most_visible_side(self, pose_landmarks):
        if self.most_visible_side != '':
            return self.most_visible_side

        # Extract joints from both sides
        right_joints = self.get_landmarks(
            pose_landmarks,
            ['right_shoulder', 'right_hip', 'right_knee', 'right_ankle', 'right_foot_index']
        )
        left_joints = self.get_landmarks(
            pose_landmarks,
            ['left_shoulder', 'left_hip', 'left_knee', 'left_ankle', 'left_foot_index']
        )
        right_visibility = 0
        left_visibility = 0
        for right_joint, left_joint in zip(right_joints, left_joints):
            right_visibility += right_joint[3]
            left_visibility += left_joint[3]

        if right_visibility < left_visibility:
            self.most_visible_side = 'left_'
        else:
            self.most_visible_side = 'right_'
        
        return self.most_visible_side

    def get_landmarks(self, pose_landmarks, landmarks):
        return [[
            pose_landmarks.landmark[self.landmark_names[landmark_name]].x,
            pose_landmarks.landmark[self.landmark_names[landmark_name]].y,
            pose_landmarks.landmark[self.landmark_names[landmark_name]].z,
            pose_landmarks.landmark[self.landmark_names[landmark_name]].visibility
        ] for landmark_name in landmarks]

    def analyse_landmark_stack(self, pose_landmarks_stack):
        # TODO: https://learnopencv.com/ai-fitness-trainer-using-mediapipe/, use this to determine feedback based on angles

        # this needs to vary with frame stack size
        moving_threshold = 0.01 # move to __init__
        start_head_height = self.get_landmarks(pose_landmarks_stack[0], ['nose'])[0][1]
        end_head_height = self.get_landmarks(pose_landmarks_stack[-1], ['nose'])[0][1]

        most_visible_side = self.__get_most_visible_side(pose_landmarks_stack[-1])

        squat_details = self.determine_squat_stage(pose_landmarks_stack[-1], most_visible_side)

        if squat_details[0] == 'Unsure':
            if abs(end_head_height - start_head_height) >= moving_threshold:
                # heights are relative to top of window so swap
                start_head_height, end_head_height = end_head_height, start_head_height
                if end_head_height < start_head_height:
                    squat_details[0] = 'Descending'
                else:
                    squat_details[0] = 'Ascending'

        return squat_details

    def determine_squat_stage(self, pose_landmarks, joint_side):
        if pose_landmarks == None:
            return ['Undetected', '', '', '']

        shoulder, hip, knee, ankle, toe = self.get_landmarks(
            pose_landmarks,
            [joint_side + 'shoulder', joint_side + 'hip', joint_side + 'knee', joint_side + 'ankle', joint_side + 'foot_index']
        )

        joints = [toe, ankle, knee]
        toe_ankle_knee = None
        if self.__check_confidence(self.min_confidence_threshold, joints):
            toe_ankle_knee = self.__calc_angle(joints)

        joints = [ankle, knee, hip]
        ankle_knee_hip = None
        if self.__check_confidence(self.min_confidence_threshold, joints):
            ankle_knee_hip = self.__calc_angle(joints)

        joints = [knee, hip, shoulder]
        knee_hip_shoulder = None
        if self.__check_confidence(self.min_confidence_threshold, joints):
            knee_hip_shoulder = self.__calc_angle(joints)

        stage = 'Unsure'
        if ankle_knee_hip != None:
            if abs(ankle_knee_hip - self.standing_angle) <= self.standing_threshold:
                stage = 'Standing'
            elif ankle_knee_hip <= self.squatting_angle + self.squatting_threshold:
                stage = 'Bottom'

        return [
            stage,
            '' if toe_ankle_knee == None else round(toe_ankle_knee),
            '' if ankle_knee_hip == None else round(ankle_knee_hip),
            '' if knee_hip_shoulder == None else round(knee_hip_shoulder),
            joint_side
        ]

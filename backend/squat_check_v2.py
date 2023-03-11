import numpy as np
import math

class SquatFormAnalyzer():
    def __init__(self,
        confidence_threshold=0.5,
    ):
        self.min_confidence_threshold = confidence_threshold
        self.main_joints = ['ankle', 'knee', 'hip', 'shoulder']
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

    def __check_confidence(self, confidence_threshold, joints):
        return all(joints) and all([joint[3] > confidence_threshold for joint in joints])

    def get_most_visible_side(self, pose_landmarks):
        if self.most_visible_side != '':
            return self.most_visible_side

        # Extract joints from both sides
        right_joints = self.get_landmarks(
            pose_landmarks,
            ['right_' + j for j in self.main_joints]
        )
        left_joints = self.get_landmarks(
            pose_landmarks,
            ['left_' + j for j in self.main_joints]
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

    def get_main_joints(self, pose_landmarks, most_visible_side):
        return self.get_landmarks(
            pose_landmarks,
            [most_visible_side + j for j in self.main_joints],
        )

    def __get_angle_with_conf(self, confidence_threshold, joints):
        if self.__check_confidence(confidence_threshold, joints):
            return self.__calc_angle(joints)
        return None

    def get_main_joint_vertical_angles(self, pose_landmarks, most_visible_side):
        ankle, knee, hip, shoulder = self.get_main_joints(pose_landmarks, most_visible_side)
        ankle_vertical = (ankle[0], 0, ankle[2], ankle[3])
        knee_vertical  = (knee[0] , 0, knee[2] , knee[3])
        hip_vertical   = (hip[0]  , 0, hip[2]  , hip[3])

        return [
            self.__get_angle_with_conf(self.min_confidence_threshold, [ankle_vertical, ankle, knee]),
            self.__get_angle_with_conf(self.min_confidence_threshold, [knee_vertical, knee, hip]),
            self.__get_angle_with_conf(self.min_confidence_threshold, [hip_vertical, hip, shoulder])
        ]

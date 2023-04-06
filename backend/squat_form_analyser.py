from collections import Counter, namedtuple

import numpy as np
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark


class MediaPipe_To_Form_Interpreter():
    def __init__(self,
        confidence_threshold=0.5,
    ):
        self.min_confidence_threshold = confidence_threshold
        self.main_joints = ['ankle', 'knee', 'hip', 'shoulder']
        self.main_joints_for_dict = [
            'left_ankle', 'right_ankle',
            'left_knee', 'right_knee',
            'left_hip', 'right_hip',
            'left_shoulder', 'right_shoulder'
        ]
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
        self.orientation_decided = False
        self.orientation = []
        self.VerticalBase = namedtuple('VerticalBase', ['x', 'y', 'z', 'visibility'])


    def __calc_angle(self, joints):
        point1, point2, point3 = joints
        radians = np.arctan2(point3.y-point2.y, point3.x-point2.x) \
                - np.arctan2(point1.y-point2.y, point1.x-point2.x)
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle


    def __check_confidence(self, confidence_threshold, joints):
        return all(joints) and all([joint.visibility > confidence_threshold for joint in joints])


    def get_most_visible_side(self, pose_landmarks):
        if self.most_visible_side == '':
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
                right_visibility += right_joint.visibility
                left_visibility += left_joint.visibility

            if right_visibility < left_visibility:
                self.most_visible_side = 'left_'
            else:
                self.most_visible_side = 'right_'

        return self.most_visible_side


    def get_landmarks(self, pose_landmarks, landmarks):
        return [
            pose_landmarks.landmark[self.landmark_names[landmark_name]
        ] for landmark_name in landmarks]


    def get_orientation_and_joint_dict(self, pose_landmarks):
        joint_dict = {
            joint_name: pose_landmarks.landmark[self.landmark_names[joint_name]]
            for joint_name in self.main_joints_for_dict
        }

        if not self.orientation_decided and len(self.orientation) < 10:
            left_shoulder, right_shoulder, \
            left_hip, right_hip, \
                = self.get_landmarks(pose_landmarks,
                    ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
                )
            # Todo, check confidence

            shoulder_depth_difference = abs(left_shoulder.z - right_shoulder.z)
            hip_depth_difference = abs(left_hip.z - right_hip.z)

            depth_threshold = 0.3

            if shoulder_depth_difference < depth_threshold or hip_depth_difference < depth_threshold:
                self.orientation.append("face_on")
            else:
                self.orientation.append("side_on")

            most_common, _ = Counter(self.orientation).most_common(1)[0]
            if len(self.orientation) == 10:
                self.orientation_decided = True
                self.orientation = most_common
            else:
                return most_common, joint_dict

        return self.orientation, joint_dict


    def get_main_joints(self, pose_landmarks, most_visible_side):
        return self.get_landmarks(
            pose_landmarks,
            [most_visible_side + j for j in self.main_joints],
        )


    def __get_angle_with_conf(self, confidence_threshold, joints):
        primary_joint = joints[0]
        vertical = self.VerticalBase(
            primary_joint.x,
            0,
            primary_joint.z,
            primary_joint.visibility
        )

        joints.insert(0, vertical)
        if self.__check_confidence(confidence_threshold, joints):
            return self.__calc_angle(joints)
        return None


    def get_main_joint_vertical_angles(self, joints):
        return [
            self.__get_angle_with_conf(self.min_confidence_threshold, [joints['ankle'], joints['knee']]),
            self.__get_angle_with_conf(self.min_confidence_threshold, [joints['knee'], joints['hip']]),
            self.__get_angle_with_conf(self.min_confidence_threshold, [joints['hip'], joints['shoulder']])
        ]


    def check_joints_are_level(self, joint1, joint2, threshold):
        return abs(joint1.y - joint2.y) <= threshold


    def check_joints_are_inline(self, joint1_left, joint1_right, joint2_left, joint2_right, threshold):
        return abs(abs(joint1_right.x - joint1_left.x) - abs(joint2_right.x - joint2_left.x)) <= threshold

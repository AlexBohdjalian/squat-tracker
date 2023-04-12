from collections import Counter, namedtuple

import numpy as np
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark


class MediaPipe_To_Form_Interpreter():
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
        self.VerticalBase = namedtuple('VerticalBase', ['x', 'y', 'z', 'visibility'])
        self.most_visible_side = []
        self.orientation = []


    def initialise_state(self):
        self.most_visible_side = []
        self.orientation = []


    def __calc_angle(self, joints):
        point1, point2, point3 = joints
        radians = np.arctan2(point3.y-point2.y, point3.x-point2.x) \
                - np.arctan2(point1.y-point2.y, point1.x-point2.x)
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle


    def check_confidence(self, confidence_threshold, joints):
        return all(joints) and all([joint.visibility > confidence_threshold for joint in joints])


    def get_joints_dict(self, pose_landmarks):
        return {
            joint_name: pose_landmarks.landmark[self.landmark_names[joint_name]]
            for joint_name in self.landmark_names.keys()
        }


    def get_most_visible_side(self, left_joints, right_joints, set_begun):
        if set_begun:
            if isinstance(self.most_visible_side, type([])):
                self.most_visible_side, _ = Counter(self.most_visible_side).most_common(1)[0]
        else:
            right_visibility = 0
            left_visibility = 0
            for right_joint, left_joint in zip(right_joints, left_joints):
                right_visibility += right_joint.visibility
                left_visibility += left_joint.visibility

            if right_visibility < left_visibility:
                self.most_visible_side.append('left_')
            else:
                self.most_visible_side.append('right_')
            
            return self.most_visible_side[-1]

        return self.most_visible_side


    def get_orientation(self, left_shoulder, right_shoulder, left_hip, right_hip, threshold):
        if isinstance(self.orientation, type([])) and len(self.orientation) < 10:
            # TODO: check confidence

            shoulder_depth_difference = abs(left_shoulder.z - right_shoulder.z)
            hip_depth_difference = abs(left_hip.z - right_hip.z)

            if shoulder_depth_difference < threshold and hip_depth_difference < threshold:
                self.orientation.append("face_on")
            else:
                self.orientation.append("side_on")

            most_common, _ = Counter(self.orientation).most_common(1)[0]
            if len(self.orientation) == 10:
                self.orientation = most_common
            else:
                return most_common

        return self.orientation


    def __get_angle_with_conf(self, confidence_threshold, joints):
        primary_joint = joints[0]
        vertical = self.VerticalBase(
            primary_joint.x,
            0,
            primary_joint.z,
            primary_joint.visibility
        )

        joints.insert(0, vertical)
        if self.check_confidence(confidence_threshold, joints):
            return self.__calc_angle(joints)
        return None


    def get_main_joint_vertical_angles(self, joints):
        return [
            self.__get_angle_with_conf(self.min_confidence_threshold, [joints['ankle'], joints['knee']]),
            self.__get_angle_with_conf(self.min_confidence_threshold, [joints['knee'], joints['hip']]),
            self.__get_angle_with_conf(self.min_confidence_threshold, [joints['hip'], joints['shoulder']])
        ]


    def joints_in_starting_position(
        self,
        knee_vertical_angle,
        hip_vertical_angle,
        knee_angle_range,
        hip_angle_range
    ):
        return knee_angle_range[0] <= knee_vertical_angle <= knee_angle_range[1] and \
            hip_angle_range[0] <= hip_vertical_angle <= hip_angle_range[1]


    def check_joints_are_level(self, joint1, joint2, threshold):
        return abs(joint1.y - joint2.y) <= threshold


    def check_joints_are_vertically_aligned(self, left_joint1, right_joint1, left_joint2, right_joint2, threshold):
        joint1_mid = abs(right_joint1.x + abs(right_joint1.x - left_joint1.x) / 2)
        joint2_mid = abs(right_joint2.x + abs(right_joint2.x - left_joint2.x) / 2)
        return abs(joint1_mid - joint2_mid) <= threshold

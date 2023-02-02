import numpy as np
import math
import mediapipe as mp

class SquatFormAnalyzer():
    def __init__(self, angle_threshold, min_confidence_threshold):
        self.stages = ['Standing', 'Descending', 'Bottom', 'Ascending']
        self.angle_threshold = angle_threshold
        self.min_confidence_threshold = min_confidence_threshold
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
        


    def calc_angle(sefl, joints):
        point1, point2, point3 = joints
        radians = np.arctan2(point3[1]-point2[1], point3[0]-point2[0]) \
                - np.arctan2(point1[1]-point2[1], point1[0]-point2[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle >180.0:
            angle = 360-angle
            
        return angle


    def angle_of_singleline(self, point1, point2):
        """ Calculate angle of a single line """
        x_diff = point2[0] - point1[0]
        y_diff = point2[1] - point1[1]
        return math.degrees(math.atan2(y_diff, x_diff))


    def dist_xy(self, point1, point2):
        """ Euclidean distance between two points point1, point2 """
        diff_point1 = (point1[0] - point2[0]) ** 2
        diff_point2 = (point1[1] - point2[1]) ** 2
        return (diff_point1 + diff_point2) ** 0.5


    def point_position(self, point, line_pt_1, line_pt_2):
        """ Left or Right position of the point from a line """
        value = (line_pt_2[0] - line_pt_1[0]) * (point[1] - line_pt_1[1]) - \
                (line_pt_2[1] - line_pt_1[1]) * (point[0] - line_pt_1[0])
        if value >= 0:
            return "left"
        return "right"


    def get_landmarks(self, pose_landmarks, landmarks):
        return [[
            pose_landmarks.landmark[self.landmark_names[landmark_name]].x,
            pose_landmarks.landmark[self.landmark_names[landmark_name]].y,
            pose_landmarks.landmark[self.landmark_names[landmark_name]].z,
            pose_landmarks.landmark[self.landmark_names[landmark_name]].visibility
        ] for landmark_name in landmarks]


    def check_confidence(self, confidence_threshold, joints):
        return all(joints) and \
           all([joint[3] > confidence_threshold for joint in joints])


    def analyse_landmark_stack(self, pose_landmarks_stack):
        start_hip_height = self.get_landmarks(pose_landmarks_stack[-1], ['left_hip'])[0][1]
        end_hip_height = self.get_landmarks(pose_landmarks_stack[0], ['left_hip'])[0][1]
        squat_details = self.determine_squat_stage(pose_landmarks_stack[-1], True)

        if squat_details[0] == 'Unsure':
            if end_hip_height > start_hip_height:
                squat_details[0] = 'Ascending'
            else:
                squat_details[0] = 'Descending'

        return squat_details


    def determine_squat_stage(self, pose_landmarks, get_angles=False):
        if pose_landmarks == None:
            return ['Undetected', '', '', '']

        # For now, this assumes visually symmetrical squat        
        # Extract the hip, knee and ankle joints
        shoulder, hip, knee, ankle, toe = self.get_landmarks(
            pose_landmarks,
            ['left_shoulder', 'left_hip', 'left_knee', 'left_ankle', 'left_foot_index']
        )

        if get_angles:
            joints = [toe, ankle, knee]
            toe_ankle_knee = None
            if self.check_confidence(self.min_confidence_threshold, joints):
                toe_ankle_knee = self.calc_angle(joints)

        joints = [ankle, knee, hip]
        ankle_knee_hip = None
        if self.check_confidence(self.min_confidence_threshold, joints):
            ankle_knee_hip = self.calc_angle(joints)

        if get_angles:
            joints = [knee, hip, shoulder]
            knee_hip_shoulder = None
            if self.check_confidence(self.min_confidence_threshold, joints):
                knee_hip_shoulder = self.calc_angle(joints)

        # Move this to __init__
        standing_threshold = 10
        standing_angle = 180
        squatting_threshold = 10
        squatting_angle = 90

        # knee-joint angle = ankle_knee_hip
        # hip-joint angle = knee_hip_shoulder

        # change this to return:
        # replace angle with 'na'? if any of the points don't meet a confidence threshold
        # ['stage', toe-ankle-knee, ankle-knee-hip, knee-hip-shoulder]
        # # USE LOGIC IN:
        # # https://medium.com/mlearning-ai/an-easy-guide-for-pose-estimation-with-googles-mediapipe-a7962de0e944

        stage = 'Unsure'
        if ankle_knee_hip != None:
            if abs(ankle_knee_hip - standing_angle) <= standing_threshold:
                stage = 'Standing'
            elif ankle_knee_hip <= squatting_angle:
                stage = 'Bottom'
        
        if get_angles:
            return [
                stage,
                '' if toe_ankle_knee == None else round(toe_ankle_knee),
                '' if ankle_knee_hip == None else round(ankle_knee_hip),
                '' if knee_hip_shoulder == None else round(knee_hip_shoulder)
            ]
        else: return [stage, '', '', '']


    def evaluate_form():
        print()
        # angle of hip-ankle line should be close to perpendicular with floor
        # angle of knee-ankle line should be close to perpendicular with floor
        # should ideally be stacking multiple frames (markov property)
            # use a function that is called on first frames (24) only to determine mean head height
                # using mean head height and foot height we have min and max
        # normalise head height to be zero at mean head height
            # so,
                # if normalised height is < 0: downward motion
                # vice versa


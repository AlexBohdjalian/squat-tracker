import cv2
import mediapipe as mp


class MediaPipeDetector:
    def __init__(self):
        # self.mp_pose = mp.solutions.pose
        self.pose = mp.solutions.pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)


    def make_prediction(self, image):
        # To improve performance, mark the image as not writeable.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)

        # Only care about pose_positions relative to the body, not the world
        return results.pose_landmarks

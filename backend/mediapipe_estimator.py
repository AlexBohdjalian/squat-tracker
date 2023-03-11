import cv2
import mediapipe as mp


class MediaPipeDetector:
    def __init__(
        self,
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks= True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
        ):
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )


    def make_prediction(self, image):
        image.flags.writeable = False
        results = self.pose.process(image)

        # Only care about pose_positions relative to the body, not the world
        return results.pose_landmarks

import mediapipe as mp


class MediaPipeDetector:
    def __init__(
        self,
        model_complexity=1,
        smooth_landmarks= True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
        ):
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )


    def make_prediction(self, image):
        image.flags.writeable = False
        return self.pose.process(image).pose_landmarks

import cv2
from mediapipe_estimator import MediaPipeDetector
import tempfile
import mediapipe as mp

class SquatFormAnalyser():
    def __init__(self, model_complexity):
        self.pose_estimator = MediaPipeDetector(model_complexity=model_complexity)

    def analyse(self, video_path, show_output=False):
        cap = cv2.VideoCapture(video_path)

        temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(
            temp_video_file.name,
            cv2.VideoWriter_fourcc(*'mp4v'),
            cap.get(cv2.CAP_PROP_FPS),
            (width, height)
        )

        final_summary = {}
        while True:
            success, frame = cap.read()
            if not success:
                break

            landmarks = self.pose_estimator.make_prediction(frame)
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                landmarks,
                mp.solutions.pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style()
            )

            # TODO: Do form analysis

            if show_output:
                cv2.imshow('Video', frame)
                cv2.waitKey(1)
            out.write(frame)
        cv2.destroyAllWindows()
        cap.release()
        out.release()

        # Create final summary
        final_summary = {'goodReps': 4, 'badReps': 3, 'mistakesMade': [{'rep': 1, 'mistakes': ['Poor Depth']}], 'finalComments': "This is from the non-live video processing script"}

        return temp_video_file, final_summary

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

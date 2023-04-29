import cv2
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf

# Optimized to be run in the browser environment using Tensorflow.js with WebGL support or on-device with TF Lite.
# Tuned to be robust on detecting fitness/fast movement with difficult poses and/or motion blur.
# Most suitable for detecting the pose of a single person who is 3ft ~ 6ft away from a device’s webcam that captures the video stream.
# Focus on detecting the pose of the person who is closest to the image center and ignore the other people who are in the image frame (i.e. background people rejection).
# The model predicts 17 human keypoints of the full body even when they are occluded. For the keypoints which are outside of the image frame, the model will emit low confidence scores. A confidence threshold (recommended default: 0.3) can be used to filter out unconfident predictions.

class PoseNetDetector:
    def __init__(self, p_model_index=0):
        models = [
            "backend/assets/lite-model_movenet_singlepose_lightning_3.tflite",
            "backend/assets/lite-model_movenet_singlepose_thunder_tflite_float16_4.tflite",
        ]
        model_path = models[p_model_index]
        if 'thunder' in model_path:
            self.input_size = 256
            self.dtype = tf.uint8
        else:
            self.input_size = 192
            self.dtype = tf.float32

        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()


    def draw_key_points(self, p_frame, key_points):
        y, x, c = p_frame.shape
        shaped = np.squeeze(np.multiply(key_points, [y, x, 1]))

        for kp in shaped:
            ky, kx, kp_conf = kp
            if kp_conf > self.confidence_threshold:
                cv2.circle(p_frame, (int(kx), int(ky)), 4, (0, 255, 0), -1)


    def draw_connections(self, p_frame, key_points):
        y, x, c = p_frame.shape
        shaped = np.squeeze(np.multiply(key_points, [y, x, 1]))

        for edge, color in self.EDGES.items():
            p1, p2 = edge
            y1, x1, c1 = shaped[p1]
            y2, x2, c2 = shaped[p2]

            if (c1 > self.confidence_threshold) & (c2 > self.confidence_threshold):
                cv2.line(p_frame, (int(x1), int(y1)),
                        (int(x2), int(y2)), (0, 0, 255), 2)


    def make_prediction(self, p_image):
        frame = p_image

        # Reshape image
        img = frame.copy()
        img = tf.image.resize_with_pad(np.expand_dims(img, axis=0), self.input_size, self.input_size)
        input_image = tf.cast(img, dtype=self.dtype)

        # Setup input
        input_image = tf.cast(input_image, dtype=self.dtype)

        # Make predictions
        self.interpreter.set_tensor(self.input_details[0]['index'], input_image.numpy())
        self.interpreter.invoke()
        key_points_with_scores = self.interpreter.get_tensor(self.output_details[0]['index'])

        # Rendering
        # self.draw_connections(frame, key_points_with_scores)
        # self.draw_key_points(frame, key_points_with_scores)

        # return frame

        return key_points_with_scores

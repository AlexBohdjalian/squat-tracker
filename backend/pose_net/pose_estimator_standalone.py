import cv2
import numpy as np
import tensorflow as tf

# Optimized to be run in the browser environment using Tensorflow.js with WebGL support or on-device with TF Lite.
# Tuned to be robust on detecting fitness/fast movement with difficult poses and/or motion blur.
# Most suitable for detecting the pose of a single person who is 3ft ~ 6ft away from a device’s webcam that captures the video stream.
# Focus on detecting the pose of the person who is closest to the image center and ignore the other people who are in the image frame (i.e. background people rejection).
# The model predicts 17 human keypoints of the full body even when they are occluded. For the keypoints which are outside of the image frame, the model will emit low confidence scores. A confidence threshold (recommended default: 0.3) can be used to filter out unconfident predictions.


def draw_key_points(p_frame, key_points, confidence_threshold):
    y, x, c = p_frame.shape
    shaped = np.squeeze(np.multiply(key_points, [y, x, 1]))

    for kp in shaped:
        ky, kx, kp_conf = kp
        if kp_conf > confidence_threshold:
            cv2.circle(p_frame, (int(kx), int(ky)), 4, (0, 255, 0), -1)


def draw_connections(p_frame, key_points, edges, confidence_threshold):
    y, x, c = p_frame.shape
    shaped = np.squeeze(np.multiply(key_points, [y, x, 1]))

    for edge, color in edges.items():
        p1, p2 = edge
        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]

        if (c1 > confidence_threshold) & (c2 > confidence_threshold):
            cv2.line(p_frame, (int(x1), int(y1)),
                     (int(x2), int(y2)), (0, 0, 255), 2)

EDGES = {
    (0, 1): 'm',
    (0, 2): 'c',
    (1, 3): 'm',
    (2, 4): 'c',
    (0, 5): 'm',
    (0, 6): 'c',
    (5, 7): 'm',
    (7, 9): 'm',
    (6, 8): 'c',
    (8, 10): 'c',
    (5, 6): 'y',
    (5, 11): 'm',
    (6, 12): 'c',
    (11, 12): 'y',
    (11, 13): 'm',
    (13, 15): 'm',
    (12, 14): 'c',
    (14, 16): 'c'
}

# consider using thunder and lowering the framerate
models = [
    "backend/assets/lite-model_movenet_singlepose_lightning_3.tflite",
    "backend/assets/lite-model_movenet_singlepose_thunder_tflite_float16_4.tflite",
]
model_path = models[0]
if 'thunder' in model_path:
    input_size = 256
else:
    input_size = 192
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

cap = cv2.VideoCapture(0)
frame_count = 0
frame_skip = 5
while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_count += 1

    if frame_count % frame_skip != 0:
        cv2.imshow('MoveNet Lightning', frame)
        continue

    # Reshape image
    img = frame.copy()
    img = tf.image.resize_with_pad(np.expand_dims(img, axis=0), input_size, input_size)
    input_image = tf.cast(img, dtype=tf.float32)

    # Setup input and output
    input_image = tf.cast(input_image, dtype=tf.float32)
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Make predictions
    interpreter.set_tensor(input_details[0]['index'], input_image.numpy())
    interpreter.invoke()
    key_points_with_scores = interpreter.get_tensor(output_details[0]['index'])

    # Rendering
    draw_connections(frame, key_points_with_scores, EDGES, 0.4)
    draw_key_points(frame, key_points_with_scores, 0.4)

    cv2.imshow('MoveNet Lightning', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

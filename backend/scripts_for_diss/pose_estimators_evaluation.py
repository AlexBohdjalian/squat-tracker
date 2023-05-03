import time

import cv2
import matplotlib.patches as patches
import mediapipe as mp
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from mediapipe_estimator import MediaPipeDetector
# from openpose import pyopenpose as op

BODY_PARTS = {"Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
              "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
              "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
              "LEye": 15, "REar": 16, "LEar": 17, "Background": 18}

POSE_PAIRS = [["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
              ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
              ["Neck", "RHip"], ["RHip", "RKnee"], [
    "RKnee", "RAnkle"], ["Neck", "LHip"],
    ["LHip", "LKnee"], ["LKnee", "LAnkle"], [
    "Neck", "Nose"], ["Nose", "REye"],
    ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"]]

MOVENET_KEYPOINT_DICT = {
    'nose': 0,
    'left_eye': 1,
    'right_eye': 2,
    'left_ear': 3,
    'right_ear': 4,
    'left_shoulder': 5,
    'right_shoulder': 6,
    'left_elbow': 7,
    'right_elbow': 8,
    'left_wrist': 9,
    'right_wrist': 10,
    'left_hip': 11,
    'right_hip': 12,
    'left_knee': 13,
    'right_knee': 14,
    'left_ankle': 15,
    'right_ankle': 16
}

KEYPOINT_EDGE_INDS_TO_COLOR = {
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

landmark_drawing_spec = mp.solutions.drawing_styles.get_default_pose_landmarks_style()


def mediapipe_calc_angle(landmarks):
    joint1, joint2, joint3 = [landmarks.landmark[joint_index]
                              for joint_index in [27, 25, 23]]

    # Create vectors from joint2 to joint1 and joint2 to joint3
    vector1 = np.array([joint1.x - joint2.x, joint1.y -
                       joint2.y, joint1.z - joint2.z])
    vector2 = np.array([joint3.x - joint2.x, joint3.y -
                       joint2.y, joint3.z - joint2.z])

    # Calculate the dot product and magnitudes of the vectors
    dot_product = np.dot(vector1, vector2)
    magnitude1_squared = np.dot(vector1, vector1)
    magnitude2_squared = np.dot(vector2, vector2)

    # Calculate the angle between the vectors in radians
    radians = np.arccos(
        dot_product / np.sqrt(magnitude1_squared * magnitude2_squared))

    # Convert radians to degrees
    angle = np.rad2deg(radians)

    return angle


def openpose_calc_angle(points, threshold=0.2):
    left_ankle_confidence = points[BODY_PARTS['LAnkle']][2]
    left_knee_confidence = points[BODY_PARTS['LKnee']][2]
    left_hip_confidence = points[BODY_PARTS['LHip']][2]

    if (left_ankle_confidence > threshold
        and left_knee_confidence > threshold
        and left_hip_confidence > threshold
    ):
        left_ankle = points[BODY_PARTS['LAnkle']][:2]
        left_knee = points[BODY_PARTS['LKnee']][:2]
        left_hip = points[BODY_PARTS['LHip']][:2]
        ba = left_ankle - left_knee
        bc = left_hip - left_knee

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle) * 180 / np.pi
        return angle
    else:
        return None


# def draw_openpose_keypoints_and_lines(frame, points, threshold=0.2):
#     for pair in POSE_PAIRS:
#         partFrom, partTo = pair
#         idFrom, idTo = BODY_PARTS[partFrom], BODY_PARTS[partTo]

#         if points[idFrom][2] > threshold and points[idTo][2] > threshold:
#             x1, y1 = points[idFrom][:2]
#             x2, y2 = points[idTo][:2]

#             cv2.circle(frame, (x1, y1), 3, (0, 255, 0), thickness=-1)
#             cv2.circle(frame, (x2, y2), 3, (0, 255, 0), thickness=-1)
#             cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

#     return frame


def movenet_calc_angle(keypoints_and_edges_for_disp):
    left_ankle = keypoints_and_edges_for_disp[0][MOVENET_KEYPOINT_DICT["left_ankle"]]
    left_knee = keypoints_and_edges_for_disp[0][MOVENET_KEYPOINT_DICT["left_knee"]]
    left_hip = keypoints_and_edges_for_disp[0][MOVENET_KEYPOINT_DICT["left_hip"]]

    a = np.array(left_ankle)
    b = np.array(left_knee)
    c = np.array(left_hip)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)


def _keypoints_and_edges_for_display(keypoints_with_scores,
                                     height,
                                     width,
                                     keypoint_threshold=0.11):
    """Returns high confidence keypoints and edges for visualization.

    Args:
      keypoints_with_scores: A numpy array with shape [1, 1, 17, 3] representing
        the keypoint coordinates and scores returned from the MoveNet model.
      height: height of the image in pixels.
      width: width of the image in pixels.
      keypoint_threshold: minimum confidence score for a keypoint to be
        visualized.

    Returns:
      A (keypoints_xy, edges_xy, edge_colors) containing:
        * the coordinates of all keypoints of all detected entities;
        * the coordinates of all skeleton edges of all detected entities;
        * the colors in which the edges should be plotted.
    """
    keypoints_all = []
    keypoint_edges_all = []
    edge_colors = []
    num_instances, _, _, _ = keypoints_with_scores.shape
    for idx in range(num_instances):
        kpts_x = keypoints_with_scores[0, idx, :, 1]
        kpts_y = keypoints_with_scores[0, idx, :, 0]
        kpts_scores = keypoints_with_scores[0, idx, :, 2]
        kpts_absolute_xy = np.stack(
            [width * np.array(kpts_x), height * np.array(kpts_y)], axis=-1)
        kpts_above_thresh_absolute = kpts_absolute_xy[
            kpts_scores > keypoint_threshold, :]
        keypoints_all.append(kpts_above_thresh_absolute)

        for edge_pair, color in KEYPOINT_EDGE_INDS_TO_COLOR.items():
            if (kpts_scores[edge_pair[0]] > keypoint_threshold and
                    kpts_scores[edge_pair[1]] > keypoint_threshold):
                x_start = kpts_absolute_xy[edge_pair[0], 0]
                y_start = kpts_absolute_xy[edge_pair[0], 1]
                x_end = kpts_absolute_xy[edge_pair[1], 0]
                y_end = kpts_absolute_xy[edge_pair[1], 1]
                line_seg = np.array([[x_start, y_start], [x_end, y_end]])
                keypoint_edges_all.append(line_seg)
                edge_colors.append(color)
    if keypoints_all:
        keypoints_xy = np.concatenate(keypoints_all, axis=0)
    else:
        keypoints_xy = np.zeros((0, 17, 2))

    if keypoint_edges_all:
        edges_xy = np.stack(keypoint_edges_all, axis=0)
    else:
        edges_xy = np.zeros((0, 2, 2))
    return keypoints_xy, edges_xy, edge_colors


def draw_prediction_on_image(
        image, keypoints_and_edges_for_disp, crop_region=None, close_figure=False,
        output_image_height=None):
    """Draws the keypoint predictions on image.

    Args:
      image: A numpy array with shape [height, width, channel] representing the
        pixel values of the input image.
      keypoints_with_scores: A numpy array with shape [1, 1, 17, 3] representing
        the keypoint coordinates and scores returned from the MoveNet model.
      crop_region: A dictionary that defines the coordinates of the bounding box
        of the crop region in normalized coordinates (see the init_crop_region
        function below for more detail). If provided, this function will also
        draw the bounding box on the image.
      output_image_height: An integer indicating the height of the output image.
        Note that the image aspect ratio will be the same as the input image.

    Returns:
      A numpy array with shape [out_height, out_width, channel] representing the
      image overlaid with keypoint predictions.
    """
    height, width, _ = image.shape
    aspect_ratio = float(width) / height
    fig, ax = plt.subplots(figsize=(12 * aspect_ratio, 12))
    # To remove the huge white borders
    fig.tight_layout(pad=0)
    ax.margins(0)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    plt.axis('off')

    im = ax.imshow(image)
    line_segments = LineCollection([], linewidths=(4), linestyle='solid')
    ax.add_collection(line_segments)
    # Turn off tick labels
    scat = ax.scatter([], [], s=60, color='#FF1493', zorder=3)

    (keypoint_locs, keypoint_edges,
     edge_colors) = keypoints_and_edges_for_disp

    line_segments.set_segments(keypoint_edges)
    line_segments.set_color(edge_colors)
    if keypoint_edges.shape[0]:
        line_segments.set_segments(keypoint_edges)
        line_segments.set_color(edge_colors)
    if keypoint_locs.shape[0]:
        scat.set_offsets(keypoint_locs)

    if crop_region is not None:
        xmin = max(crop_region['x_min'] * width, 0.0)
        ymin = max(crop_region['y_min'] * height, 0.0)
        rec_width = min(crop_region['x_max'], 0.99) * width - xmin
        rec_height = min(crop_region['y_max'], 0.99) * height - ymin
        rect = patches.Rectangle(
            (xmin, ymin), rec_width, rec_height,
            linewidth=1, edgecolor='b', facecolor='none')
        ax.add_patch(rect)

    fig.canvas.draw()
    image_from_plot = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    image_from_plot = image_from_plot.reshape(
        fig.canvas.get_width_height()[::-1] + (3,))
    plt.close(fig)
    if output_image_height is not None:
        output_image_width = int(output_image_height / height * width)
        image_from_plot = cv2.resize(
            image_from_plot, dsize=(output_image_width, output_image_height),
            interpolation=cv2.INTER_CUBIC)
    return image_from_plot


def draw_movenet_keypoints_and_lines(image, keypoints_and_edges_for_disp):
    display_image = tf.expand_dims(image, axis=0)
    display_image = tf.cast(tf.image.resize_with_pad(
        display_image, 1280, 1280), dtype=tf.int32)
    return draw_prediction_on_image(
        np.squeeze(display_image.numpy(), axis=0),
        keypoints_and_edges_for_disp
    )


def draw_angle(frame, angle):
    return cv2.putText(frame, str(round(angle)), (0, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)


def evaluate_model(method, model, show_output=False):
    print(f'Evaluating: {method}')
    elapsed_time = process_video(method, video_path, model, show_output)
    print(f"Time taken for {method}: {elapsed_time:.2f} seconds")
    return elapsed_time


def process_video(method, video_path, model, show_output):
    cap = cv2.VideoCapture(video_path)
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    start_time = time.time()
    extra_time = 0

    while cap.isOpened():
        # if method == "posenet":
        #     # NOTE: posenet is not well documented and typically relies on old incompatible code
        #     input_image, _, output_scale = posenet.read_cap(
        #         cap,
        #         scale_factor=0.4,
        #         output_stride=model[1]
        #     )
        #     heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = sess.run(
        #         model[0],
        #         feed_dict={'image:0': input_image}
        #     )
        #     _, _, keypoint_coords = posenet.decode_multiple_poses(
        #         heatmaps_result.squeeze(axis=0),
        #         offsets_result.squeeze(axis=0),
        #         displacement_fwd_result.squeeze(axis=0),
        #         displacement_bwd_result.squeeze(axis=0),
        #         output_stride=output_stride,
        #         min_pose_score=0.25)
        #     # scale keypoint co-ordinate to output scale
        #     keypoint_coords *= output_scale
        # else:
        ret, frame = cap.read()

        if not ret:
            break

        if method == "mediapipe":
            output = model.make_prediction(frame)
            if output is not None:
                # Calculate angle
                angle = mediapipe_calc_angle(output)
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    output,
                    mp.solutions.pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=landmark_drawing_spec
                )
                extra_time -= time.time()
                frame = draw_angle(frame, angle)
                extra_time += time.time()

        # elif method == "openpose":
            # model.setInput(cv2.dnn.blobFromImage(
            #     frame, 1.0, (frame_width, frame_height), (127.5, 127.5, 127.5), swapRB=True, crop=False))
            # output = model.forward()

            # points = []
            # for i in range(len(BODY_PARTS)):
            #     heatmap = output[0, i, :, :]
            #     _, conf, _, point = cv2.minMaxLoc(heatmap)
            #     x = (frame_width * point[0]) / output.shape[3]
            #     y = (frame_height * point[1]) / output.shape[2]
            #     points.append((int(x), int(y), conf))
            # frame = draw_openpose_keypoints_and_lines(frame, points)

            # angle = openpose_calc_angle(points)
            # if angle is not None:
            #     extra_time -= time.time()
            #     frame = draw_angle(frame, angle)
            #     extra_time += time.time()
            # datum = op.Datum()
            # datum.cvInputData = frame
            # opWrapper.emplaceAndPop([datum])

            # Draw the skeleton on the frame
            # frame = datum.cvOutputData

            # # Extract joint keypoints
            # keypoints = datum.poseKeypoints
            # angle = openpose_calc_angle(keypoints)
            # if angle is not None:
            #     extra_time -= time.time()
            #     frame = draw_angle(frame, angle)
            #     extra_time += time.time()

        elif method == "movenet_thunder":
            input_image = tf.expand_dims(frame, axis=0)
            input_image = tf.cast(tf.image.resize_with_pad(
                input_image, 256, 256), dtype=tf.int32)
            keypoints = model(input_image)['output_0']
            keypoints_and_edges_for_disp = _keypoints_and_edges_for_display(
                keypoints, frame_height, frame_width)
            frame = draw_movenet_keypoints_and_lines(frame, keypoints_and_edges_for_disp)

            angle = movenet_calc_angle(keypoints_and_edges_for_disp)
            if angle is not None:
                extra_time -= time.time()
                frame = draw_angle(frame, angle)
                extra_time += time.time()

        elif method == "movenet_lightning":
            input_image = tf.expand_dims(frame, axis=0)
            input_image = tf.cast(tf.image.resize_with_pad(
                input_image, 192, 192), dtype=tf.int32)
            keypoints = model(input_image)['output_0']
            keypoints_and_edges_for_disp = _keypoints_and_edges_for_display(
                keypoints, frame_height, frame_width)
            frame = draw_movenet_keypoints_and_lines(frame, keypoints_and_edges_for_disp)

            angle = movenet_calc_angle(keypoints_and_edges_for_disp)
            if angle is not None:
                extra_time -= time.time()
                frame = draw_angle(frame, angle)
                extra_time += time.time()

        if show_output:
            extra_time -= time.time()
            if not method.startswith('movenet'):
                frame = cv2.resize(frame, (frame_width // 2, frame_height // 2))
            cv2.imshow(method, frame)
            cv2.waitKey(1)
            extra_time += time.time()

    elapsed_time = time.time() - start_time - extra_time
    cap.release()
    cv2.destroyAllWindows()
    return elapsed_time


if __name__ == "__main__":
    video_path = "../assets/goblet_squat.mp4"

    # OpenPose Setup
    # openpose_model = cv2.dnn.readNetFromTensorflow("./assets/graph_opt.pb")  
    # evaluate_model('openpose', openpose_model)
    # del openpose_model
    # opWrapper = op.WrapperPython()
    # opWrapper.configure({"model_folder": "./assets/OPEN_POSE_MODELS_FOLDER/"})
    # opWrapper.start()

    # print('OpenPose Done')

    # MediaPipe Pose model
    mp_pose_classifier_0 = MediaPipeDetector(model_complexity=0)
    evaluate_model('mediapipe', mp_pose_classifier_0, show_output=True)
    del mp_pose_classifier_0

    mp_pose_classifier_1 = MediaPipeDetector(model_complexity=1)
    evaluate_model('mediapipe', mp_pose_classifier_1, show_output=True)
    del mp_pose_classifier_1

    mp_pose_classifier_2 = MediaPipeDetector(model_complexity=2)
    evaluate_model('mediapipe', mp_pose_classifier_2, show_output=True)
    del mp_pose_classifier_2

    print('MediaPipe Done')

    # MoveNet Thunder model
    movenet_thunder_model = hub.load(
        "https://tfhub.dev/google/movenet/singlepose/thunder/4")
    movenet_thunder_model = movenet_thunder_model.signatures['serving_default']
    evaluate_model('movenet_thunder', movenet_thunder_model, show_output=True)
    del movenet_thunder_model

    # MoveNet Lightning model
    movenet_lightning_model = hub.load(
        "https://tfhub.dev/google/movenet/singlepose/lightning/4")
    movenet_lightning_model = movenet_lightning_model.signatures['serving_default']
    evaluate_model('movenet_lightning', movenet_lightning_model, show_output=True)
    del movenet_lightning_model

    print('MoveNet Done')

    # # PoseNet model
    # sess = tf.compat.v1.Session()
    # model_cfg, model_outputs = posenet.load_model(101, sess)
    # output_stride = model_cfg['output_stride']
    # print('PoseNet loaded')

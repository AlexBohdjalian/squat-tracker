import pickle
import socket
from typing import Tuple
import cv2
import numpy as np
import struct


def convert_data_to_cv2image(image_data, willSave=False):
    nparr = np.frombuffer(image_data, np.uint8)
    open_cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if willSave:
        cv2.imwrite("backend/assets/processedImage.jpg", open_cv_img)

    return open_cv_img


def resize_with_pad(image: np.array, 
                    new_shape: Tuple[int, int], 
                    padding_color: Tuple[int] = (255, 255, 255)) -> np.array:
    original_shape = (image.shape[1], image.shape[0])
    ratio = float(max(new_shape))/max(original_shape)
    new_size = tuple([int(x*ratio) for x in original_shape])
    image = cv2.resize(image, new_size)
    delta_w = new_shape[0] - new_size[0]
    delta_h = new_shape[1] - new_size[1]
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)
    image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=padding_color)
    return image


def send_image(image_path):
    # Open the image file
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect(("localhost", 8888))

    # Send and receive the data
    print(f'Sending 1 frames...')
    client_socket.sendall(struct.pack("!i", 1))
    client_socket.sendall(image_data)  # use resize

    # Receive the output from the server
    output = client_socket.recv(1000000)

    # Close the connection with the server
    client_socket.close()

    convert_data_to_cv2image(output, True)


def send_video(video_path):
    # Open the video file
    # video = cv2.VideoCapture(0)
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 8888))

    # Send and receive the data
    print(f'Sending {total_frames} frames...')
    num_frames_bytes = struct.pack("!i", total_frames)
    client_socket.sendall(num_frames_bytes)

    frames = []
    while True:
        ret, frame = video.read()
        if not ret:
            break
        resized_frame = frame
        _, img_encoded = cv2.imencode('.jpg', resized_frame)
        client_socket.sendall(img_encoded.tobytes())

        data = client_socket.recv(1000)
        key_point_pred = pickle.loads(data)

        draw_key_points(frame, key_point_pred, 0.4)
        draw_connections(frame, key_point_pred, 0.4, EDGES)

        cv2.imshow("Processed frame", frame)
        cv2.waitKey(1)

        frames.append(frame)


    print(f"Received {len(frames)} frames back.")
    # Close the connection with the server
    client_socket.close()
    video.release()

    # for frame in frames:
    #     cv2.imshow("frame", frame)
    #     cv2.waitKey(10) # doesn't account for frame rate too well


def draw_key_points(p_frame, key_points, confidence_threshold):
    y, x, c = p_frame.shape
    shaped = np.squeeze(np.multiply(key_points, [y, x, 1]))

    for kp in shaped:
        ky, kx, kp_conf = kp
        if kp_conf > confidence_threshold:
            cv2.circle(p_frame, (int(kx), int(ky)), 4, (0, 255, 0), -1)


def draw_connections(p_frame, key_points, confidence_threshold, EDGES):
    y, x, c = p_frame.shape
    shaped = np.squeeze(np.multiply(key_points, [y, x, 1]))

    for edge, color in EDGES.items():
        p1, p2 = edge
        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]

        if (c1 > confidence_threshold) & (c2 > confidence_threshold):
            cv2.line(p_frame, (int(x1), int(y1)),
                    (int(x2), int(y2)), (0, 0, 255), 2)


if __name__ == '__main__':
    image_path = "backend/assets/pose_test_image.png"
    video_path = "backend/assets/pose_test_video.mp4"
    squat_video_path = "backend/assets/squat_test_video.mp4"
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
    # send_image(image_path)
    send_video(video_path)
    # send_video(squat_video_path)
    

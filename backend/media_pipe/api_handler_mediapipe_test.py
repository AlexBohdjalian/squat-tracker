import pickle
import socket
from typing import Tuple
import cv2
import numpy as np
import struct
import mediapipe as mp


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
    client_socket.sendall(image_data)

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
    print(f'Sending frames...')

    frames = []
    while True:
        ret, frame = video.read()
        if not ret:
            break
        resized_frame = frame#resize_with_pad(frame, (256, 256))
        _, img_encoded = cv2.imencode('.jpg', resized_frame)
        client_socket.sendall(img_encoded.tobytes())

        data = client_socket.recv(10000) # check how much is needed here

        pose_landmarks = pickle.loads(data)

        # Draw the pose annotation on the image.
        frame.flags.writeable = True
        mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        cv2.imshow('MediaPipe Pose', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frames.append(frame)

    client_socket.sendall(struct.pack("!i", -2))

    print(f"Received {len(frames)} frames back.")

    # Close the connection with the server
    client_socket.close()
    video.release()


if __name__ == '__main__':
    image_path = "backend/assets/pose_test_image.png"
    video_path = "backend/assets/pose_test_video.mp4"
    squat_video_path = "backend/assets/squat_test_video.mp4"
    
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_pose = mp.solutions.pose       
    
    # send_image(image_path)
    send_video(video_path)
    # send_video(squat_video_path)
    

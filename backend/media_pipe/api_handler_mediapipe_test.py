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


# Delete this?
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


def draw_text(img, text,
          font=cv2.FONT_HERSHEY_PLAIN,
          pos=(0, 0),
          font_scale=3,
          font_thickness=2,
          text_color=(0, 255, 0),
          text_color_bg=(0, 0, 0)
          ):
    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
    cv2.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness)

    return text_size


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

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 8888))

    # Send and receive the data
    print(f'Sending frames...')
    cv2.namedWindow("Mediapipe Pose", cv2.WINDOW_NORMAL)

    frames = []
    while True:
        ret, frame = video.read()
        if not ret:
            break

        _, img_encoded = cv2.imencode('.jpg', frame)
        client_socket.sendall(img_encoded.tobytes())

        data = client_socket.recv(1000000) # check how much is needed here

        pose_landmarks, squat_details = pickle.loads(data)

        # Draw the pose annotation on the image.
        frame.flags.writeable = True
        mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        draw_text(frame, squat_details[0], font_scale=4)
        draw_text(frame, 'Toe-Heel-Knee angle: ' + str(squat_details[1]), pos=(0, 40))
        draw_text(frame, 'Heel-Knee-Hip angle: ' + str(squat_details[2]), pos=(0, 70))
        draw_text(frame, 'Knee-Hip-Shoulder: ' + str(squat_details[3]), pos=(00, 100))

        cv2.imshow('MediaPipe Pose', cv2.resize(frame, (960, 540)))
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
    big_squat_video_path = "backend/assets/big_squat_test_video.mp4"
    
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_pose = mp.solutions.pose       
    
    # send_image(image_path)
    # send_video(video_path)
    send_video(squat_video_path)
    # send_video(big_squat_video_path)
    

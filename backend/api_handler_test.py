import socket
import cv2
import numpy as np
import struct


def convert_data_to_cv2image(image_data, willSave):
    nparr = np.frombuffer(image_data, np.uint8)
    opencv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if willSave:
        cv2.imwrite("backend/assets/processedImage.jpg", opencv_img)

    return opencv_img


def send_image(image_path):
    # Open the image file
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # Create a socket object
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    clientsocket.connect(("localhost", 8888))

    # Send the image data to the server
    clientsocket.sendall(image_data)

    # Receive the output from the server
    output = clientsocket.recv(1000000)

    # Close the connection with the server
    clientsocket.close()

    convert_data_to_cv2image(output, True)


def send_video(video_path):
    # Open the video file
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create a socket object
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(("localhost", 8888))

    # Send and recieve the data
    print(f'Sending {total_frames} frames...')
    num_frames_bytes = struct.pack("!i", total_frames)
    clientsocket.sendall(num_frames_bytes)

    frames = []
    while True:
        ret, frame = video.read()
        if not ret:
            break
        _, img_encoded = cv2.imencode('.jpg', frame)
        clientsocket.sendall(img_encoded.tobytes())
        
        frames_data = clientsocket.recv(1000000)
        frame = convert_data_to_cv2image(frames_data, True)

        if total_frames != -1:
            frames.append(frame)
        else:
            cv2.imshow("Processed frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    print(f"Recieved {len(frames)} frames back.")
    # Close the connection with the server
    clientsocket.close()
    video.release()

    for frame in frames:
        cv2.imshow("frame", frame)
        cv2.waitKey(10) # doesnt account for frame rate too well


if __name__ == '__main__':
    image_path = "backend/assets/pose_test_image.png"
    video_path = "backend/assets/pose_test_video.mp4"
    # send_image(image_path)
    send_video(video_path)

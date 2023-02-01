import socket
from pose_estimator import PoseNetDetector
import numpy as np
import cv2
import struct
import pickle
import time


def convert_data_to_cv2image(image_data):
    nparr = np.frombuffer(image_data, np.uint8)
    cv2_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return cv2_image


def listen_for_data():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    PORT = 8888
    server_socket.bind(("localhost", PORT))

    # Start listening for incoming connections
    server_socket.listen(5)
    server_socket.settimeout(1.0)

    print(f"Listening on port {PORT}...")

    while True:
        # Establish a connection with a client (while allowing keyboard interrupts)
        try:
            (client_socket, address) = server_socket.accept()
        except socket.timeout as e:
            continue

        print('Connection accepted...')
        start_time = time.time()

        # Receive the number of frames
        num_frames_bytes = client_socket.recv(4)
        num_frames = struct.unpack("!i", num_frames_bytes)[0]
        if num_frames == -1:
            print('Video feed detected. Limiting to 10000 frames...')
            num_frames = 10000

        for i in range(num_frames):
            # Receive data from the client
            data = client_socket.recv(1000000)
            image = convert_data_to_cv2image(data)
            print(f'Received {i + 1}/{num_frames} frames...', end='\r')

            # Process then send the data
            results = pose_detector.make_prediction(image)
            client_socket.send(pickle.dumps(results))

        # Close the connection with the client
        print(f"\nDone in {round(time.time() - start_time, 3)}.")
        client_socket.close()


if __name__ == '__main__':
    pose_detector = PoseNetDetector(0)
    listen_for_data()

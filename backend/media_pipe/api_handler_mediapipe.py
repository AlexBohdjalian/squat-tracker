import socket
from mediapipe_estimator import MediaPipeDetector
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

    server_open = True
    while server_open:
        # Establish a connection with a client (while allowing keyboard interrupts)
        try:
            (client_socket, address) = server_socket.accept()
        except socket.timeout as e:
            continue

        print('Connection accepted...')
        start_time = time.time()

        frame_count = 1
        while True:
            # Receive data from the client
            data = client_socket.recv(100000)
            if data == b'\xff\xff\xff\xfe':
                break
            elif data == b'\xff\xff\xff\xfd':
                print('Stopping server.')
                server_open = False
                break

            # Convert the image
            image = convert_data_to_cv2image(data)

            # Process then send the data
            results = pose_detector.make_prediction(image)
            client_socket.send(pickle.dumps(results))

            print(f'Received {frame_count} frames...', end='\r')
            frame_count += 1

        # Close the connection with the client
        print(f"\nDone in {round(time.time() - start_time, 3)}.")
        client_socket.close()


if __name__ == '__main__':
    pose_detector = MediaPipeDetector()
    listen_for_data()

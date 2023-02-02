import socket
from mediapipe_estimator import MediaPipeDetector
from squat_check import SquatFormAnalyzer
import numpy as np
import cv2
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
    server_socket.bind(('localhost', PORT))

    # Start listening for incoming connections
    server_socket.listen(5)
    server_socket.settimeout(1.0)

    print(f"Listening on {server_socket.getsockname()}")

    server_open = True
    while server_open:
        # Establish a connection with a client (while allowing keyboard interrupts)
        try:
            (client_socket, address) = server_socket.accept()
        except socket.timeout as e:
            continue

        print('Connection accepted...')
        start_time = time.time()

        last_squat_details = ['Unsure', '', '' , '']
        results_stack = []
        frame_count = 1
        while True:
            # Receive data from the client
            data = client_socket.recv(1000000)
            if data == b'\xff\xff\xff\xfe':
                break
            elif data == b'\xff\xff\xff\xfd':
                print('Stopping server.')
                server_open = False
                break

            # Process then send the data
            image = convert_data_to_cv2image(data)
            results = pose_detector.make_prediction(image)

            if len(results_stack) > 0 \
                and len(results_stack) % frame_stack == 0:
                squat_details = form_analyser.analyse_landmark_stack(results_stack)
                last_squat_details = squat_details
                results_stack = []
            else:
                if results == None:
                    results_stack = []
                else:
                    results_stack.append(results)
                squat_details = last_squat_details

            client_socket.send(pickle.dumps((results, squat_details)))

            print(f'Received {frame_count} frames...', end='\r')
            frame_count += 1

        # Close the connection with the client
        client_socket.close()
        print(f"\nDone in {round(time.time() - start_time, 3)}s")



if __name__ == '__main__':
    pose_detector = MediaPipeDetector()
    form_analyser = SquatFormAnalyzer(0.01, 0.5)
    frame_stack = 5
    listen_for_data()

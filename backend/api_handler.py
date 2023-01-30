import socket
from pose_estimator import PoseNetDetector
import numpy as np
import cv2
import struct
import pickle


def convert_data_to_cv2image(image_data):
    nparr = np.frombuffer(image_data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


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

        # Receive the number of frames
        num_frames_bytes = client_socket.recv(4)
        num_frames = struct.unpack("!i", num_frames_bytes)[0]
        if num_frames == -1:
            print('Video feed detected. Limiting to 10000 frames...')
            num_frames = 10000

        # print(f'Receiving {num_frames} frames...')

        for i in range(num_frames):
            # Receive data from the client
            data = client_socket.recv(1000000)
            image = convert_data_to_cv2image(data)
            print(f'Received {i + 1}/{num_frames} frames...', end='\r')

            # Process the data
            key_points_pred = pose_detector.make_prediction(image)
            client_socket.send(pickle.dumps(key_points_pred))


            # success, image_data = cv2.imencode('.jpg', output)

            # if success:
                # Send the output back to the client
            #     client_socket.send(image_data.tobytes())
            # else:
            #     raise ValueError('Error encoding image')

        # Close the connection with the client
        print('Done. Listening...')
        client_socket.close()


if __name__ == '__main__':
    pose_detector = PoseNetDetector(1)
    listen_for_data()

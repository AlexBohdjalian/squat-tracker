import socket
from pose_estimator import PoseNetDetector
import numpy as np
import cv2
import struct


pose_detector = PoseNetDetector()

def convert_data_to_cv2image(image_data):
    nparr = np.frombuffer(image_data, np.uint8)
    opencv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return opencv_img

def listen_for_data():
    # Create a socket object
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    PORT = 8888
    serversocket.bind(("localhost", PORT))

    # Start listening for incoming connections
    serversocket.listen(5)

    print(f"Listening on port {PORT}...")

    while True:
        # Establish a connection with a client
        (clientsocket, address) = serversocket.accept()

        # Recieve the number of frames
        num_frames_bytes = clientsocket.recv(4)
        num_frames = struct.unpack("!i", num_frames_bytes)[0]
        if num_frames == -1:
            print('Video feed detected. Limiting to 10000 frames...')
            num_frames = 10000

        print(f'Receiving {num_frames} frames...')

        for i in range(num_frames):
            # Receive data from the client
            data = clientsocket.recv(1000000)
            image = convert_data_to_cv2image(data)

            # Process the data
            output = pose_detector.make_prediction(image)
            success, image_data = cv2.imencode('.jpg', output)

            if success:
                # Send the output back to the client
                clientsocket.send(image_data.tobytes())
            else:
                raise ValueError('Error encoding image')


        # Close the connection with the client
        clientsocket.close()


if __name__ == '__main__':
    listen_for_data()

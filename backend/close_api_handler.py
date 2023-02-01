import socket
import struct

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 8888))

client_socket.sendall(struct.pack('!i', -3))

client_socket.close()

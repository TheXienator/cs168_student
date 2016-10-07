import socket
import sys
# The socket constructor accepts a few arguments; the defaults are fine for this class.
if len(sys.argv) != 3:
	print("python basic_client.py ip port")
else:
	client_socket = socket.socket()
	IP = sys.argv[1]
	port = int(sys.argv[2])
	client_socket.connect((IP, port))
	msg = raw_input()
	client_socket.send(msg)
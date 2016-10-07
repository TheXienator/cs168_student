import socket
import sys

if len(sys.argv) != 2:
	print("python basic_server.py port")
else:
	server_socket = socket.socket()
	server_socket.bind(("localhost", int(sys.argv[1])))
	server_socket.listen(5)
	while True:
		(new_socket, address) = server_socket.accept()
		msg = new_socket.recv(256)
		print msg
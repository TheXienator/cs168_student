import socket
import sys
<<<<<<< HEAD
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
=======

class BasicClient(object):

    def __init__(self, address, port):
        self.address = address
        self.port = int(port)
        self.socket = socket.socket()

    def send(self, message):
        self.socket.connect((self.address, self.port))
        self.socket.send(message)

args = sys.argv
if len(args) != 3:
    print "Please supply a server address and port."
    sys.exit()
client = BasicClient(args[1], args[2])
msg = raw_input()
client.send(msg)
>>>>>>> upstream/master

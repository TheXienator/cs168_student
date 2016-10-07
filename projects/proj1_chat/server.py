import socket
import sys
import select
import utils

SOCKET_LIST = []
NAMES = {} # Socket : Name
ROOMS = {} # Room : [Socket]
SOCKET_BUFFERS = {} # Socket : Buffer

def chat_server():
    if len(sys.argv) != 2:
        print "Usage: python server.py port"
        sys.exit(1)
    port = int(sys.argv[1])

    server_socket = socket.socket()
    server_socket.bind(("localhost", port))
    server_socket.listen(5)

    SOCKET_LIST.append(server_socket)
    while True:
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST, [], [])
        for sock in ready_to_read:
            if sock == server_socket:
                (new_socket, address) = server_socket.accept()
                SOCKET_LIST.append(new_socket)
                SOCKET_BUFFERS[new_socket] = ""
                msg = new_socket.recv(utils.MESSAGE_LENGTH)
                NAMES[new_socket] = msg.rstrip()
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(utils.MESSAGE_LENGTH - len(SOCKET_BUFFERS[sock]))
                    if not data:
                        leaveRoom(sock)
                        removeSock(sock)
                        continue

                    total = SOCKET_BUFFERS[sock] + data
                    if len(total) < utils.MESSAGE_LENGTH:
                        SOCKET_BUFFERS[sock] = total
                    else:
                        SOCKET_BUFFERS[sock] = total[utils.MESSAGE_LENGTH:]
                        data = total[:utils.MESSAGE_LENGTH]

                        if data[0] == "/":
                            data = data.rstrip().split(" ")
                            command = data[0]

                            if command in ["/join", "/create"] and len(data) > 1:
                                roomName = data[1]
                                if command == "/join":
                                    join(sock, roomName.rstrip())
                                else:
                                    create(sock, roomName.rstrip())
                            elif command == "/list":
                                listRooms(sock)
                        else:
                            message = data.rstrip()
                            broadcast(server_socket, sock, "\r" + '[' + NAMES[sock] + '] ' + message)
                except:
                    broadcast(server_socket, sock, "Something bad happened")
                    continue

def broadcast(server_socket, sock, msg):
    for socket in SOCKET_LIST:
        if socket != server_socket and socket != sock and sameRoom(socket, sock):
            try:
                socket.send(msg.ljust(utils.MESSAGE_LENGTH))
            except:
                leaveRoom(socket)
                removeSock(socket)

def removeSock(sock):
    sock.close()
    if sock in SOCKET_LIST:
        SOCKET_LIST.remove(sock)
    if sock in SOCKET_BUFFERS:
        del SOCKET_BUFFERS[sock]
    if sock in NAMES:
        del NAMES[sock]

def sameRoom(socket1, socket2):
    for room in ROOMS:
        sockets = ROOMS[room]
        if socket1 in sockets and socket2 in sockets:
            return True
    return False

def leaveRoom(sock):
    for room in ROOMS:
        sockets = ROOMS[room]
        if sock in sockets:
            sockets.remove(sock)
            for socket in sockets:
                msg = "\r" + utils.SERVER_CLIENT_LEFT_CHANNEL.format(NAMES[sock])
                socket.send(msg.ljust(utils.MESSAGE_LENGTH))
            return

def listRooms(sock):
    msg = ""
    for room in ROOMS:
        msg += room + "\n"
    sock.send(msg.ljust(utils.MESSAGE_LENGTH))

def hasRoom(sock):
    for room in ROOMS:
        sockets = ROOMS[room]
        if sock in sockets:
            return True
    return False

def join(sock, roomName):
    if roomName in ROOMS:
        leaveRoom(sock)
        msg = "\r" + utils.SERVER_CLIENT_JOINED_CHANNEL.format(NAMES[sock])
        for socket in ROOMS[roomName]:
            socket.send(msg.ljust(utils.MESSAGE_LENGTH))
        ROOMS[roomName] += [sock]
    else:
        msg = "\r" + utils.SERVER_NO_CHANNEL_EXISTS.format(roomName)
        if not hasRoom(sock):
            msg = "error" + msg
        sock.send(msg.ljust(utils.MESSAGE_LENGTH))

def create(sock, roomName):
    if roomName in ROOMS:
        msg = "\r" + utils.SERVER_CHANNEL_EXISTS.format(roomName)
        if not hasRoom(sock):
            msg = "error" + msg
        sock.send(msg.ljust(utils.MESSAGE_LENGTH))
    else:
        leaveRoom(sock)
        ROOMS[roomName] = [sock]

if __name__ == "__main__":
    sys.exit(chat_server())
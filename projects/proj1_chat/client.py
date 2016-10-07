import socket
import sys
import select
import utils

def chat_client():
    if len(sys.argv) != 4:
        print "Usage: python client.py name host port"
        sys.exit(1)
    name = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])

    client_socket = socket.socket()
    client_socket.settimeout(2)
    try:
        client_socket.connect((host, port))
    except:
        print utils.CLIENT_CANNOT_CONNECT.format(host, port)
        return

    client_socket.send(name.ljust(utils.MESSAGE_LENGTH))
    writePrefix()
    hasChannel = False
    buff = ""
    while True:
        socket_list = [sys.stdin, client_socket]
        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])
        for sock in ready_to_read:
            if sock == client_socket:
                data = sock.recv(utils.MESSAGE_LENGTH - len(buff))
                if not data:
                    print utils.CLINET_SERVER_DISCONNECTED.format(host, port)
                    client_socket.close()
                    return
                
                total = buff + data
                if len(total) < utils.MESSAGE_LENGTH:
                    buff = total
                else:
                    data = total[:utils.MESSAGE_LENGTH]
                    buff = total[utils.MESSAGE_LENGTH:]
                    data = data.rstrip()

                    if data[:6] == "error\r":
                        hasChannel = False
                        data = data[5:]
                    if data: # data can be "" if the user calls /list and there are no rooms
                        sys.stdout.write(data + "\n") 
                    writePrefix()
            else:
                msg = sock.readline() # sock would be sys.stdin
                msg = msg.rstrip()
                sections = msg.split(" ")

                if msg and msg[0] == "/" and sections[0] not in ["/create", "/join", "/list"]:
                    print utils.SERVER_INVALID_CONTROL_MESSAGE.format(sections[0])
                    writePrefix()
                    continue
                elif sections[0] == "/create" and len(sections) == 1:
                    print utils.SERVER_CREATE_REQUIRES_ARGUMENT
                    writePrefix()
                    continue
                elif sections[0] == "/join" and len(sections) == 1:
                    print utils.SERVER_JOIN_REQUIRES_ARGUMENT
                    writePrefix()
                    continue

                if sections[0] in ["/create", "/join"]:
                    hasChannel = True

                if not hasChannel and msg[:5] != "/list":
                    print utils.SERVER_CLIENT_NOT_IN_CHANNEL
                else:
                    client_socket.send(msg.ljust(utils.MESSAGE_LENGTH))
                if sections[0] != "/list":
                    writePrefix()

def writePrefix():
  sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX); sys.stdout.flush() 

if __name__ == "__main__":
    sys.exit(chat_client())
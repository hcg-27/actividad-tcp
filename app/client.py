from tcp.socket_tcp import SocketTCP
from .config import *


def main():

    #s = SocketTCP()
    #s.connect((SERVER_IP, SERVER_PORT))
    #print(s)

    client_socketTCP = SocketTCP()
    client_socketTCP.connect((SERVER_IP, SERVER_PORT))
    print(client_socketTCP)
    # test 1
    message = "Mensje de len=16".encode()
    client_socketTCP.send(message)
    # test 2
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)
    # test 3
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)
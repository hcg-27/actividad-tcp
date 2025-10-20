from tcp.socket_tcp import SocketTCP
from .config import *


def main():

    s = SocketTCP()

    s.bind((SERVER_IP, SERVER_PORT))

    s.accept()

    print(s)

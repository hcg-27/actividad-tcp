from tcp.socket_tcp import SocketTCP
from .config import *


def main():

    s = SocketTCP()

    s.connect((SERVER_IP, SERVER_PORT))

    print(s)
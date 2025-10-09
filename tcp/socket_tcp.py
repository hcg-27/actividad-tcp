from socket import socket, AF_INET, SOCK_DGRAM

class SocketTCP:
    def __init__(self) -> None:
        self.udp: socket = socket(AF_INET, SOCK_DGRAM) 
        self.source: tuple[str, int] = ("", 0)
        self.destination: tuple[str, int] = ("", 0)
        self.sequence: int = 0


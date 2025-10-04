from .converter import TCPSegmentConverter
from socket import socket, AF_INET, SOCK_DGRAM


class SocketTCP:
    def __init__(self) -> None:
        self.socket: socket = socket(AF_INET, SOCK_DGRAM)
        self.origin: tuple[str, int] = ("", 0)
        self.destination: tuple[str, int] = ("", 0)
        self.seq: int = 0
        self.converter: TCPSegmentConverter = TCPSegmentConverter()

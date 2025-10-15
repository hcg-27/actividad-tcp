import socket
from pathlib import Path
from .config import *
from tcp.segment import TCPSegment
from tcp.codec import SegmentCodec as codec
from tcp.socket_tcp import SocketTCP

def main() -> None:

    client_socketTCP = SocketTCP()
    client_socketTCP.connect((SERVER_IP, SERVER_PORT))

    # Mostrar estado del socket
    print(client_socketTCP)

    # Test 1
    message = "Mensje de len=16".encode()
    client_socketTCP.send(message)

    # Test 2
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)

    # Test 3
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)

    # Cerrar Conexion
    client_socketTCP.close()

    # Mostrar estado del socket
    print(client_socketTCP)

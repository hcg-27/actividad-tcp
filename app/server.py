import socket 
from .config import *
from tcp.segment import TCPSegment
from tcp.codec import SegmentCodec as codec
from tcp.socket_tcp import SocketTCP

def main() -> None:

    server_socket = SocketTCP()
    server_socket.bind((SERVER_IP, SERVER_PORT))
    connection_socketTCP, new_address = server_socket.accept()

    # Mostrar estado del socket
    print(connection_socketTCP)

    # Test 1
    buff_size = 16
    full_message = connection_socketTCP.recv(buff_size)
    print("Test 1 received:", full_message)
    if full_message == "Mensje de len=16".encode():
        print("Test 1: Passed")
    else:
        print("Test 1: Failed")

    # Test 2
    buff_size = 19
    full_message = connection_socketTCP.recv(buff_size)
    print("Test 2 received:", full_message)
    if full_message == "Mensaje de largo 19".encode():
        print("Test 2: Passed")
    else:
        print("Test 2: Failed")

    # Test 3
    buff_size = 14
    message_part_1 = connection_socketTCP.recv(buff_size)
    message_part_2 = connection_socketTCP.recv(buff_size)
    print("Test 3 received:", message_part_1 + message_part_2)
    if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode():
        print("Test 3: Passed")
    else:
        print("Test 3: Failed")
   
    # Esperar cierre de conexión
    connection_socketTCP.recv_close()

    # Mostrar estado del socket
    print(connection_socketTCP)

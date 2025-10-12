import socket 
from .config import *
from tcp.segment import TCPSegment
from tcp.codec import SegmentCodec as codec
from tcp.socket_tcp import SocketTCP

def main() -> None:

    # Inicializar socket
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.bind((SERVER_IP, SERVER_PORT))

    #print("...Server UP...")

    #try:
    #    # Esperar mensajes
    #    while True:
    #        data, _ = s.recvfrom(BUFF_SIZE)
    #        segment = codec.parse_segment(data)

    #        # Imprimir mensajes en pantalla
    #        print(segment)
    #except KeyboardInterrupt:
    #    print("\n...Server DOWN...")

    # ================================

    #server = SocketTCP()
    #server.bind((SERVER_IP, SERVER_PORT))
    #conn, addr = server.accept()

    #print(addr, conn.source, conn.seq)

    # =================================

    server_socket = SocketTCP()
    server_socket.bind((SERVER_IP, SERVER_PORT))
    connection_socketTCP, new_address = server_socket.accept()

    #import time
    #try:
    #    print("Esperando netem")
    #    while True:
    #        time.sleep(1)
    #except KeyboardInterrupt:
    #    print("continuando operacion")

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
    print(connection_socketTCP)

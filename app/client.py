import socket
from pathlib import Path
from .config import *
from tcp.segment import TCPSegment
from tcp.codec import SegmentCodec as codec
from tcp.socket_tcp import SocketTCP

def main() -> None:

    # Inicializar socket
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #print("...Client UP...")

    #while True:

    #    # Esperar input del usuario
    #    try:
    #        line = input().encode(encoding='utf-8')
    #    except EOFError:
    #        print("...Client DOWN..")
    #        break

    #    # Enviar input al servidor de a 16 bytes por vez
    #    sent = 0
    #    to_send = len(line)
    #    while sent < to_send:
    #    
    #        data = line[sent:sent+16]
    #        segment = TCPSegment(seq=118, data=data)
    #        s.sendto(codec.create_segment(segment), (SERVER_IP, SERVER_PORT))

    #        # Preparar próxima iteración
    #        sent += 16

    # =================================

    #client = SocketTCP()
    #client.connect((SERVER_IP, SERVER_PORT))

    #print(client.destination, client.source, client.seq)

    # =================================
    client_socketTCP = SocketTCP()
    client_socketTCP.connect((SERVER_IP, SERVER_PORT))

    # Busy-waiting para esperar netem
    import time
    try:
        print("esperando netem")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("continuando operacion")
    
    # Test 1
    message = "Mensje de len=16".encode()
    client_socketTCP.send(message)

    # Test 2
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)

    # Test 3
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)

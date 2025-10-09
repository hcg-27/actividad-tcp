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

    server = SocketTCP()
    server.bind((SERVER_IP, SERVER_PORT))
    conn, addr = server.accept()

    print(addr, conn.source, conn.seq)


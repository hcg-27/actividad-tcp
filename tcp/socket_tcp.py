from random import randint
from socket import socket, AF_INET, SOCK_DGRAM
from .constants import *
from .segment import TCPSegment
from .codec import SegmentCodec

class SocketTCP:
    def __init__(self) -> None:
        self.udp: socket = socket(AF_INET, SOCK_DGRAM) 
        self.source: tuple[str, int] = ("", 0)
        self.destination: tuple[str, int] = ("", 0)
        self.seq: int = 0
        self.codec: SegmentCodec = SegmentCodec()

    def bind(self, address: tuple[str, int]) -> None:
        self.udp.bind(address)
        self.source = self.udp.getsockname() 

    def connect(self, address: tuple[str, int]) -> None:

        # Seleccionar número de secuencia inicial
        self.seq = randint(0, 100)

        # Crear SYN
        syn = self.codec.create_segment(TCPSegment(syn=True, seq=self.seq))

        # Enviar SYN al destino
        self.udp.sendto(syn, address)
        
        # Esperar SYN-ACK y dirección de destino
        data = self.udp.recvfrom(DGRAM_SIZE)
        syn_ack, destination = self.codec.parse_segment(data[0]), data[1]

        if syn_ack.syn and syn_ack.ack and syn_ack.seq == self.seq + 1:

            # Ajustar número de secuencia
            self.seq = syn_ack.seq + 1   

            # Ajustar dirección de destino
            self.destination = destination

        # Crear ACK
        ack = self.codec.create_segment(TCPSegment(ack=True, seq=self.seq))

        # Enviar ACK al destino
        self.udp.sendto(ack, self.destination)

        # Actualizar dirección de origen
        self.source = self.udp.getsockname()


    def accept(self) -> tuple["SocketTCP", tuple[str, int]]:

        # Esperar SYN
        data = self.udp.recvfrom(DGRAM_SIZE)
        syn, destination = self.codec.parse_segment(data[0]), data[1]

        if syn.syn:

            # Crear y configurar nuevo socket
            new_socket = SocketTCP()
            new_socket.seq = syn.seq + 1
            new_socket.destination = destination
            new_socket.bind(("0.0.0.0", 0))

        # Crear SYN+ACK
        syn_ack = self.codec.create_segment(TCPSegment(syn=True, ack=True, seq=new_socket.seq))

        # Enviar SYN+ACK al destino
        new_socket.udp.sendto(syn_ack, new_socket.destination)

        # Esperar ACK
        data = new_socket.udp.recvfrom(DGRAM_SIZE)
        ack = new_socket.codec.parse_segment(data[0])

        if ack.ack and ack.seq == new_socket.seq + 1:

            # Ajustar número de secuencia
            new_socket.seq = ack.seq

        return new_socket, new_socket.destination

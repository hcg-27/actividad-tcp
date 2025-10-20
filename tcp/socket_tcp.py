import math
import random
import time
from socket import socket, AF_INET, SOCK_DGRAM
from .consts import *
from .codec import SegmentCodec
from .segment import TCPSegment, check


class SocketTCP:

    def __init__(self) -> None:
        
        self.udp: socket = socket(AF_INET, SOCK_DGRAM)
        self.source: tuple[str, int] = ("", 0)
        self.destination: tuple[str, int] = ("", 0)
        self.seq: int = 0
        self.codec: SegmentCodec = SegmentCodec()
        self.waiting_first: bool = True
        self.received: int = 0
        self.to_receive: int | float = math.inf
    
    def __repr__(self) -> str:
        
        repr = "SocketTCP("
        repr += f"socket={self.udp}, "
        repr += f"source={self.source}, "
        repr += f"destination={self.destination}, "
        repr += f"seq={self.seq}, "
        repr += f"received={self.received}, "
        repr += f"to_received={self.to_receive})"

        return repr
    
    def bind(self, address: tuple[str, int]) -> None:

        self.udp.bind(address)
        self.source = self.udp.getsockname()

    def connect(self, address: tuple[str, int]) -> None:

        self.seq = random.randint(0, 100)

        syn = TCPSegment(syn=True, seq=self.seq)
        syn_data = self.codec.create_segment(syn)

        # Establecer destino
        self.destination = address

        # Establecer timeout
        self.udp.settimeout(TIMEOUT_SECONDS)

        while True:
                
            try:

                # Enviar ACK
                self.udp.sendto(syn_data, self.destination)

                # Esperar SYN+ACK
                data, destination = self.udp.recvfrom(DGRAM_SIZE)
                syn_ack = self.codec.parse_segment(data)

                if check(syn_ack, "sa") and syn_ack.seq == self.seq + 1:

                    # Ajustar número de secuencia
                    self.seq = syn_ack.seq + 1

                    # Ajustar dirección de destino
                    self.destination = destination

                    break
            
            except TimeoutError:

                continue
        
        ack = TCPSegment(ack=True, seq=self.seq)
        ack_data = self.codec.create_segment(ack)

        conn_attempts = 0
        while conn_attempts < MAX_CONN_ATTEMPTS:

            # Enviar ACK    
            self.udp.sendto(ack_data, self.destination)

            # Esperar un tiempo antes de volver a mandar ACK
            time.sleep(WAIT_SECONDS)

            conn_attempts += 1
        
        # Actualizar dirección de origen
        self.source = self.udp.getsockname()

    def accept(self) -> tuple["SocketTCP", tuple[str, int]]:

        data, destination = self.udp.recvfrom(DGRAM_SIZE)
        syn = self.codec.parse_segment(data)

        if check(syn, "s"):

            # Crear y configurar nuevo socket
            new_socket = SocketTCP()
            new_socket.seq = syn.seq + 1
            new_socket.destination = destination
            new_socket.bind(("0.0.0.0", 0))

        syn_ack = TCPSegment(syn=True, ack=True, seq=new_socket.seq)
        syn_ack_data = self.codec.create_segment(syn_ack)

        # Establecer timeout
        new_socket.udp.settimeout(TIMEOUT_SECONDS)

        while True:

            try:

                # Enviar SYN+ACK
                new_socket.udp.sendto(syn_ack_data, new_socket.destination)

                # Esperar ACK
                data, _ = new_socket.udp.recvfrom(DGRAM_SIZE)
                ack = self.codec.parse_segment(data)

                if check(ack, "a") and ack.seq == new_socket.seq + 1:

                    # Ajustar número de secuencia
                    new_socket.seq = ack.seq

                    break
            
            except TimeoutError:

                continue

        # Resetear timeout
        new_socket.udp.settimeout(None)

        return new_socket, new_socket.source

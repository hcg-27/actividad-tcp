import math
import random
import struct
import time
from socket import socket, AF_INET, SOCK_DGRAM
from .consts import *
from .codec import SegmentCodec
from .segment import TCPSegment, check


class SocketTCP:

    def __init__(self, debug_enabled: bool = False) -> None:
        
        self.udp: socket = socket(AF_INET, SOCK_DGRAM)
        self.source: tuple[str, int] = ("", 0)
        self.destination: tuple[str, int] = ("", 0)
        self.seq: int = 0
        self.codec: SegmentCodec = SegmentCodec()
        self.waiting_len: bool = True
        self.received: int = 0
        self.to_receive: int | float = math.inf
        self.debug_enabled: bool = debug_enabled
        self.log_number: int = 1
    
    def __repr__(self) -> str:
        
        repr = "SocketTCP("
        repr += f"socket={self.udp}, "
        repr += f"source={self.source}, "
        repr += f"destination={self.destination}, "
        repr += f"seq={self.seq}, "
        repr += f"received={self.received}, "
        repr += f"to_received={self.to_receive})"

        return repr
    
    def _clean(self) -> None:

        self.udp.close()
        self.source = ("", 0)
        self.destination = ("", 0)
        self.seq = 0
        self.received = 0
        self.to_receive = math.inf
    
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

                self.udp.sendto(syn_data, self.destination)

                # Esperar SYN+ACK
                data, destination = self.udp.recvfrom(DGRAM_SIZE)
                syn_ack = self.codec.parse_segment(data)

                if check(syn_ack, "sa", self.seq + 1):

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
   
            self.udp.sendto(ack_data, self.destination)

            # Esperar un tiempo antes de volver a mandar ACK
            time.sleep(WAIT_SECONDS)

            conn_attempts += 1
        
        # Actualizar dirección de origen
        self.source = self.udp.getsockname()

        # Resetear timeout
        self.udp.settimeout(None)

    def accept(self) -> tuple["SocketTCP", tuple[str, int]]:

        data, destination = self.udp.recvfrom(DGRAM_SIZE)
        syn = self.codec.parse_segment(data)

        if check(syn, "s", None):

            # Crear y configurar nuevo socket
            new_socket = SocketTCP(self.debug_enabled)
            new_socket.seq = syn.seq + 1
            new_socket.destination = destination
            new_socket.bind(("0.0.0.0", 0))

        syn_ack = TCPSegment(syn=True, ack=True, seq=new_socket.seq)
        syn_ack_data = self.codec.create_segment(syn_ack)

        # Establecer timeout
        new_socket.udp.settimeout(TIMEOUT_SECONDS)

        while True:

            try:

                new_socket.udp.sendto(syn_ack_data, new_socket.destination)

                # Esperar ACK
                data, _ = new_socket.udp.recvfrom(DGRAM_SIZE)
                ack = self.codec.parse_segment(data)

                if check(ack, "a", new_socket.seq + 1):

                    # Ajustar número de secuencia
                    new_socket.seq = ack.seq

                    break
            
            except TimeoutError:

                continue

        # Resetear timeout
        new_socket.udp.settimeout(None)

        return new_socket, new_socket.source
    
    def send(self, message: bytes) -> None:

        length = len(message)

        seg = TCPSegment(data=struct.pack("!Q", length), seq=self.seq)
        seg_data = self.codec.create_segment(seg)

        # Establecer timeout
        self.udp.settimeout(TIMEOUT_SECONDS)

        # Enviar largo del mensaje
        while True:

            try:

                self.udp.sendto(seg_data, self.destination)

                # Esperar ACK
                data, _ = self.udp.recvfrom(DGRAM_SIZE)
                ack  = self.codec.parse_segment(data)

                if check(ack, "a", self.seq + 1):

                    self.seq = ack.seq

                    break

                # Caso en que se perdió el último ACK del handshake
                elif check(ack, "sa", self.seq - 1):

                    # Reenviar ACK de conexión
                    conn_ack = TCPSegment(ack=True, seq=self.seq)
                    conn_ack_data = self.codec.create_segment(conn_ack)
                    
                    self.udp.sendto(conn_ack_data, self.destination)
            
            except TimeoutError:

                continue
        
        # Enviar mensaje por trozos de tamaño MSS
        sent = 0
        to_send = length
        while sent < to_send:

            try:

                seg = TCPSegment(seq=self.seq, data=message[sent:sent+MSS])
                seg_data = self.codec.create_segment(seg)

                self.udp.sendto(seg_data, self.destination)

                # Esperar ACK
                data, _ = self.udp.recvfrom(DGRAM_SIZE)
                ack = self.codec.parse_segment(data)

                if check(ack, "a", self.seq + 1):

                    self.seq = ack.seq
                    sent += MSS
                
            except TimeoutError:

                continue
        
        # Resetear timeout
        self.udp.settimeout(None)
        
    def recv(self, buff_size: int) -> bytes:

        received_message = b''
        while (self.received < self.to_receive and
               len(received_message) < buff_size):
            
            data, _ = self.udp.recvfrom(DGRAM_SIZE)
            seg = self.codec.parse_segment(data)

            if self.waiting_len and check(seg, "", self.seq):

                self.seq += 1
                self.to_receive = struct.unpack("!Q", seg.data)[0]
                self.waiting_len = False
            
            elif check(seg, "", self.seq):

                self.seq += 1
                self.received += len(seg.data)
                received_message += seg.data
            
            # Enviar ACK
            ack = TCPSegment(ack=True, seq=self.seq)
            ack_data = self.codec.create_segment(ack)

            self.udp.sendto(ack_data, self.destination)
        
        # Resetear variables si se recibio todo el mensaje
        if self.received >= self.to_receive:

            self.waiting_len = True
            self.received = 0
            self.to_receive = math.inf
        
        return received_message
    
    def close(self) -> None:

        fin = TCPSegment(fin=True, seq=self.seq)
        fin_data = self.codec.create_segment(fin)

        # Establecer timeout
        self.udp.settimeout(TIMEOUT_SECONDS)

        close_attempts = 0
        while close_attempts < MAX_CLOSE_ATTEMPTS:

            try:

                self.udp.sendto(fin_data, self.destination)

                # Esperar FIN+ACK
                data, _ = self.udp.recvfrom(DGRAM_SIZE)
                fin_ack = self.codec.parse_segment(data)

                if check(fin_ack, "af", self.seq + 1):

                    self.seq = fin_ack.seq + 1

                    break

            except TimeoutError:

                close_attempts += 1

                continue
        
        else:

            # Cerrar conexión unilateralmente
            self._clean()

            return
        
        ack = TCPSegment(ack=True, seq=self.seq)
        ack_data = self.codec.create_segment(ack)

        # Envíar ACK hasta un máximo de MAX_CLOSE_ATTEMPTS veces
        close_attempts = 0
        while close_attempts < MAX_CLOSE_ATTEMPTS:

            self.udp.sendto(ack_data, self.destination)

            time.sleep(WAIT_SECONDS)

            close_attempts += 1
        
        # Cerrar conexión
        self._clean()

        return
    
    def recv_close(self) -> None:
    
        while True:

            # Esperar FIN
            data, _ = self.udp.recvfrom(DGRAM_SIZE)
            fin = self.codec.parse_segment(data)

            if check(fin, "f", self.seq):

                self.seq += 1

                break

            elif check(fin, "", self.seq - 1):

                # Reenviar ack anterior
                seg_ack = TCPSegment(ack=True, seq=self.seq)
                seg_ack_data = self.codec.create_segment(seg_ack)

                self.udp.sendto(seg_ack_data, self.destination)

        fin_ack = TCPSegment(ack=True, fin=True, seq=self.seq)
        fin_ack_data = self.codec.create_segment(fin_ack)

        # Establecer timeout
        self.udp.settimeout(TIMEOUT_SECONDS)

        close_attempts = 0
        while close_attempts < MAX_CLOSE_ATTEMPTS:

            try:

                self.udp.sendto(fin_ack_data, self.destination)

                data, _ = self.udp.recvfrom(DGRAM_SIZE)
                ack = self.codec.parse_segment(data)

                if check(ack, "a", self.seq + 1):

                    self._clean()

                    break

            except TimeoutError:

                close_attempts += 1

                continue

        else:

            # Cerrar conexión unilateralmente
            self._clean()       

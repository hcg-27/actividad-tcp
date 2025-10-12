import struct
import math
from random import randint
from socket import socket, AF_INET, SOCK_DGRAM
from .constants import *
from .segment import TCPSegment
from .codec import SegmentCodec
from .exceptions import AttemptLimitException

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

        return new_socket, new_socket.source

    def send(self, message: bytes) -> None:

        # Obtener largo del mensaje
        length = len(message)

        # Configurar timeout de MAX_TIMEOUT
        self.udp.settimeout(MAX_TIMEOUT)

        # Enviar largo del mensaje
        attempt = 0
        while attempt < MAX_ATTEMPTS:

            try:

                segment = TCPSegment(data=struct.pack("!Q", length), seq=self.seq)
                data = self.codec.create_segment(segment)
                self.udp.sendto(data, self.destination)

                # Esperar ACK
                data = self.udp.recvfrom(DGRAM_SIZE)
                ack = self.codec.parse_segment(data[0])

                # Verificar que sea el ACK correcto
                if ack.seq == self.seq + 1:

                    self.seq = ack.seq
                    break

                else:

                    attempt +=1

            except TimeoutError:

                attempt += 1

        else:

            error_message = "Error: no se puedo enviar largo del mensaje"
            raise AttemptLimitException(error_message)


        # Enviar mensaje por trozos de 16 bytes
        attempt = 0
        sent = 0
        to_send = length
        while sent < to_send and attempt < MAX_ATTEMPTS:

            try:

                segment = TCPSegment(seq=self.seq, data=message[sent:sent+16])
                data = self.codec.create_segment(segment)
                self.udp.sendto(data, self.destination)

                # Esperar ACK
                data = self.udp.recvfrom(DGRAM_SIZE)
                ack = self.codec.parse_segment(data[0])

                # Verificar número de secuencia
                if ack.seq == self.seq + 1:

                    self.seq = ack.seq
                    sent += 16
                    
                    # Reiniciar contandor de intentos
                    attempt = 0

                else:

                    attempt += 1
            
            except TimeoutError:

                attempt += 1

        else:
            
            # Chequear si se alcanzo el máximo de intentos
            if attempt == MAX_ATTEMPTS #and to_send > sent + 16:

                error_message = "Error: no se reecibio ack del mensaje: "
                error_message += f"[{sent}:{sent+16}]"
                raise AttemptLimitException(error_message)
            
            #else:

                # Si se llega a esta parte, es porque lo único que 
                # falta es el ACK del último mensaje, que se asume
                # recebido por el destinatario
                #self.seq = len(message[sent:sent+16])

            # En caso contrario no hubo ningún error

    def recv(self, buff_size: int) -> bytes:

        received_message = b''
        while (len(received_message) < buff_size and
               self.received < self.to_receive):

            data = self.udp.recvfrom(DGRAM_SIZE)
            segment = self.codec.parse_segment(data[0])

            # Veríficar que sea el primer mensaje
            if self.waiting_first and segment.seq == self.seq:

                self.seq += 1
                self.to_receive = struct.unpack("!Q", segment.data)[0]
                self.waiting_first = False

            # Si no es el primer mensaje, verificar número de secuencia
            elif segment.seq == self.seq:

                self.seq += 1
                self.received += len(segment.data)
                print(segment.data)
                received_message += segment.data
            
            # Enviar ACK
            segment = TCPSegment(ack=True, seq=self.seq)
            data = self.codec.create_segment(segment)
            self.udp.sendto(data, self.destination)

        # Resetear variables (de ser necesario)
        if self.received >= self.to_receive:
            
            self.waiting_first = True
            self.received = 0
            self.to_receive = math.inf

        return received_message 

    def close() -> None: ...

    def recv_close() -> None: ...


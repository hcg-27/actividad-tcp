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

        if self.debug_enabled:
            print(f"Estableciendo conexión con servidor")
            print(f"Manejo de perdidas: Si")

        self.seq = random.randint(0, 100)

        syn = TCPSegment(syn=True, seq=self.seq)
        syn_data = self.codec.create_segment(syn)

        # Establecer destino
        self.destination = address

        # Establecer timeout
        self.udp.settimeout(TIMEOUT_SECONDS)

        while True:
                
            try:

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} connect: "
                    msg += f"enviando syn {syn.seq}"
                    print(msg)
                    self.log_number += 1

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

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} connect: "
                    msg += f"no llegó ack de syn {syn.seq}"
                    print(msg)
                    self.log_number += 1

                continue
        
        ack = TCPSegment(ack=True, seq=self.seq)
        ack_data = self.codec.create_segment(ack)

        conn_attempts = 0
        while conn_attempts < MAX_CONN_ATTEMPTS:

            if self.debug_enabled:
                msg = f"{self.log_number:.>5} connect: "
                msg += f"enviando ack {ack.seq} para cerrar handshake, "
                msg += f"intento: {conn_attempts + 1}"
                print(msg)
                self.log_number += 1
   
            self.udp.sendto(ack_data, self.destination)

            # Esperar un tiempo antes de volver a mandar ACK
            time.sleep(WAIT_SECONDS)

            conn_attempts += 1
        
        # Actualizar dirección de origen
        self.source = self.udp.getsockname()

        if self.debug_enabled:
            msg = f"{self.log_number:.>5} connect: "
            msg += f"conexión establecida con {self.destination}"
            print(msg)
            self.log_number += 1

        # Resetear timeout
        self.udp.settimeout(None)

    def accept(self) -> tuple["SocketTCP", tuple[str, int]]:

        if self.debug_enabled:
            print("Esperando conexión")
            print("Manejo de perdidas: Si")
            print("esperando syn")

        data, destination = self.udp.recvfrom(DGRAM_SIZE)
        syn = self.codec.parse_segment(data)

        if check(syn, "s", None):

            # Crear y configurar nuevo socket
            new_socket = SocketTCP(self.debug_enabled)
            new_socket.seq = syn.seq + 1
            new_socket.destination = destination
            new_socket.bind(("0.0.0.0", 0))

            if self.debug_enabled:
                msg = f"{self.log_number:.>5} accept: "
                msg += f"nuevo socket creado en: {new_socket.source}"
                print(msg)
                self.log_number += 1

        syn_ack = TCPSegment(syn=True, ack=True, seq=new_socket.seq)
        syn_ack_data = self.codec.create_segment(syn_ack)

        # Establecer timeout
        new_socket.udp.settimeout(TIMEOUT_SECONDS)

        while True:

            try:

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} accept: "
                    msg += f"enviando syn+ack {syn_ack.seq}"
                    print(msg)
                    self.log_number += 1

                new_socket.udp.sendto(syn_ack_data, new_socket.destination)

                # Esperar ACK
                data, _ = new_socket.udp.recvfrom(DGRAM_SIZE)
                ack = self.codec.parse_segment(data)

                if check(ack, "a", new_socket.seq + 1):

                    # Ajustar número de secuencia
                    new_socket.seq = ack.seq

                    break
            
            except TimeoutError:

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} accept: "
                    msg += f"no llegó ack de syn+ack {syn_ack.seq}"
                    print(msg)
                    self.log_number += 1

                continue

        # Resetear timeout
        new_socket.udp.settimeout(None)

        if self.debug_enabled:
            msg = f"{self.log_number:.>5} accept: "
            msg += f"conexión establecida con {new_socket.destination}"
            print(msg)
            self.log_number += 1

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

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} send: "
                    msg += f"enviando largo del mensaje"
                    print(msg)
                    self.log_number += 1

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

                    if self.debug_enabled:
                        msg = f"{self.log_number:.>5} send: "
                        msg += "reenviando último ack del handshake"
                        print(msg)
                        self.log_number += 1
                    
                    self.udp.sendto(conn_ack_data, self.destination)
            
            except TimeoutError:

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} send: "
                    msg += f"no llegó ack del largo del mensaje"
                    print(msg)
                    self.log_number += 1

                continue
        
        # Enviar mensaje por trozos de tamaño MSS
        sent = 0
        to_send = length
        while sent < to_send:

            try:

                seg = TCPSegment(seq=self.seq, data=message[sent:sent+MSS])
                seg_data = self.codec.create_segment(seg)

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} send: "
                    msg += f"enviando segmento {seg.seq}"
                    print(msg)
                    self.log_number += 1

                self.udp.sendto(seg_data, self.destination)

                # Esperar ACK
                data, _ = self.udp.recvfrom(DGRAM_SIZE)
                ack = self.codec.parse_segment(data)

                if check(ack, "a", self.seq + 1):

                    self.seq = ack.seq
                    sent += MSS
                
            except TimeoutError:

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} send :"
                    msg += f"no llegó ack de segmento {seg.seq}"
                    print(msg)
                    self.log_number += 1

                continue
        
        # Resetear timeout
        self.udp.settimeout(None)
        
    def recv(self, buff_size: int) -> bytes:

        received_message = b''
        while (self.received < self.to_receive and
               len(received_message) < buff_size):
            
            if self.debug_enabled:
                msg = f"{self.log_number:.>5} recv: "
                msg += f"esperando segmento {self.seq}"
                print(msg)
                self.log_number += 1
            
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

            if self.debug_enabled:
                msg = f"{self.log_number:.>5} recv: "
                msg += f"enviando ack de segmento {seg.seq}"
                print(msg)
                self.log_number += 1

            self.udp.sendto(ack_data, self.destination)
        
        # Resetear variables si se recibio todo el mensaje
        if self.received >= self.to_receive:

            self.waiting_len = True
            self.received = 0
            self.to_receive = math.inf

            if self.debug_enabled:
                msg = f"{self.log_number:.>5} recv: "
                msg += f"mensaje recibido en su totalidad"
                print(msg)
                self.log_number += 1
        
        return received_message
    
    def close(self) -> None:

        if self.debug_enabled:
            print("Cerrando conexión")

        fin = TCPSegment(fin=True, seq=self.seq)
        fin_data = self.codec.create_segment(fin)

        # Establecer timeout
        self.udp.settimeout(TIMEOUT_SECONDS)

        close_attempts = 0
        while close_attempts < MAX_CLOSE_ATTEMPTS:

            try:

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} close: "
                    msg += f"enviando fin {fin.seq}, "
                    msg += f"intento: {close_attempts + 1}"
                    print(msg)
                    self.log_number += 1

                self.udp.sendto(fin_data, self.destination)

                # Esperar FIN+ACK
                data, _ = self.udp.recvfrom(DGRAM_SIZE)
                fin_ack = self.codec.parse_segment(data)

                if check(fin_ack, "af", self.seq + 1):

                    self.seq = fin_ack.seq + 1

                    break

            except TimeoutError:

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} close: "
                    msg += f"no llegó ack de fin {fin.seq}"
                    print(msg)
                    self.log_number += 1

                close_attempts += 1

                continue
        
        else:

            if self.debug_enabled:
                msg = f"{self.log_number:.>5} close: "
                msg += f"cerrando conexión unilateralmente"
                print(msg)
                self.log_number += 1

            # Cerrar conexión unilateralmente
            self._clean()

            return
        
        ack = TCPSegment(ack=True, seq=self.seq)
        ack_data = self.codec.create_segment(ack)

        # Envíar ACK hasta un máximo de MAX_CLOSE_ATTEMPTS veces
        close_attempts = 0
        while close_attempts < MAX_CLOSE_ATTEMPTS:

            if self.debug_enabled:
                msg = f"{self.log_number:.>5} close: "
                msg += f"enviando último ack {ack.seq}, "
                msg += f"intento: {close_attempts + 1}"
                print(msg)
                self.log_number += 1

            self.udp.sendto(ack_data, self.destination)

            time.sleep(WAIT_SECONDS)

            close_attempts += 1
        
        # Cerrar conexión
        self._clean()

        return
    
    def recv_close(self) -> None:
    
        while True:

            if self.debug_enabled:
                msg = f"{self.log_number:.>5} recv_close: "
                msg += f"esperando fin"
                print(msg)
                self.log_number += 1

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

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} recv_close: "
                    msg += f"reenviando ack de segmento {fin.seq}"
                    print(msg)
                    self.log_number += 1

                self.udp.sendto(seg_ack_data, self.destination)

        fin_ack = TCPSegment(ack=True, fin=True, seq=self.seq)
        fin_ack_data = self.codec.create_segment(fin_ack)

        # Establecer timeout
        self.udp.settimeout(TIMEOUT_SECONDS)

        close_attempts = 0
        while close_attempts < MAX_CLOSE_ATTEMPTS:

            try:

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} recv_close: "
                    msg += f"enviando fin+ack {fin_ack.seq}, "
                    msg += f"intento: {close_attempts + 1}"
                    print(msg)
                    self.log_number += 1

                self.udp.sendto(fin_ack_data, self.destination)

                data, _ = self.udp.recvfrom(DGRAM_SIZE)
                ack = self.codec.parse_segment(data)

                if check(ack, "a", self.seq + 1):

                    self._clean()

                    break

            except TimeoutError:

                if self.debug_enabled:
                    msg = f"{self.log_number:.>5} recv_close: "
                    msg += f"no se recibio ack de fin+ack {fin_ack.seq}"
                    print(msg)
                    self.log_number += 1

                close_attempts += 1

                continue

        else:

            if self.debug_enabled:
                msg = f"{self.log_number:.>5} recv_close: "
                msg += f"cerrando conexión unilateralmente"
                print(msg)
                self.log_number += 1

            # Cerrar conexión unilateralmente
            self._clean()       

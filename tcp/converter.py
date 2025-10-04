import struct
from .segment import TCPSegment


class SegmentParseError(Exception):
    def __init__(self):
        super().__init__(f"Error parsing segment")


class TCPSegmentConverter:
    @staticmethod
    def parse_segment(segment: bytes) -> TCPSegment:
        # Unpack bytes
        flags, seq = struct.unpack_from("!BI", segment, 0)

        # Obtener flags SYN, ACK y FIN (en ese orden)
        syn: bool = bool((flags >> 2) & 1)
        ack: bool = bool((flags >> 1) & 1)
        fin: bool = bool((flags >> 0) & 1)

        # Obtener data
        data: bytes = segment[5:]

        return TCPSegment(syn=syn, ack=ack, fin=fin, seq=seq, data=data)

    @staticmethod
    def create_segment(segment: TCPSegment) -> bytes:
        # Crear flags
        flags = 0

        # Añadir SYN, ACK y FIN (en ese orden)
        flags = (flags << 1) | int(segment.syn)
        flags = (flags << 1) | int(segment.ack)
        flags = (flags << 1) | int(segment.fin)

        # Pack struct
        header: bytes = struct.pack("!BI", flags, segment.seq)

        # Retornar headers y data
        return header + segment.data

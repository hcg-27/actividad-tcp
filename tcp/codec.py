import struct
from .segment import TCPSegment

class SegmentCodec:
    @staticmethod
    def parse_segment(segment: bytes) -> TCPSegment:

        # Unpack bytes
        flags, seq = struct.unpack_from("!BI", segment, 0)

        # Recuperar flags
        syn: bool = bool((flags >> 2) & 1)
        ack: bool = bool((flags >> 1) & 1)
        fin: bool = bool((flags >> 0) & 1)

        # Obtener datos
        data: bytes = segment[5:]

        return TCPSegment(syn=syn, ack=ack, fin=fin, seq=seq, data=data)

    @staticmethod
    def create_segment(segment: TCPSegment) -> bytes: 

        # Crear flags
        flags: bytes = 0
        flags = (flags << 1) | int(segment.syn)
        flags = (flags << 1) | int(segment.ack)
        flags = (flags << 1) | int(segment.fin)

        # Pack struct
        header: bytes = struct.pack("!BI", flags, segment.seq)

        # Retornar segmento (header + data)
        return header + segment.data


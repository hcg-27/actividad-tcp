from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class TCPSegment:
    syn: bool = False
    ack: bool = False
    fin: bool = False
    seq: int = 0
    data: bytes = b''


from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class TCPSegment:

    syn: bool = False
    ack: bool = False
    fin: bool = False
    seq: int = 0
    data: bytes = b''

def check(segment: TCPSegment, flags: str):

    res = True

    match flags:
        case "saf":
            return segment.syn and segment.ack and segment.fin
        case "sa":
            return segment.syn and segment.ack and (not segment.fin)
        case "af":
            return (not segment.syn) and segment.ack and segment.fin
        case "s":
            return segment.syn and not (segment.ack or segment.fin)
        case "a":
            return segment.ack and not (segment.syn or segment.fin)
        case "f":
            return segment.fin and not (segment.syn or segment.ack)
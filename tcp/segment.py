from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class TCPSegment:

    syn: bool = False
    ack: bool = False
    fin: bool = False
    seq: int = 0
    data: bytes = b''

def check(segment: TCPSegment, flags: str, expected_seq: None | int) -> bool:

    if (expected_seq is not None) and (segment.seq != expected_seq):
        return False

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
        case _:
            return not (segment.fin or segment.ack or segment.fin)
class TCPSegment:
    def __init__(self, *, syn: bool = False, ack: bool = False,
                 fin: bool = False, seq: int = 0, data: bytes = b""):
        self.ack: bool = ack
        self.syn: bool = syn
        self.fin: bool = fin
        self.seq: int = seq
        self.data: bytes = data
    
    def __str__(self):
        return f"""TCP Segment
        \rSYN: {self.syn}
        \rACK: {self.ack}
        \rFIN: {self.fin}
        \rseq: {self.seq}
        \rdata: {self.data}"""

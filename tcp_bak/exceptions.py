class SocketTCPException(Exception): 
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

class AttemptLimitException(SocketTCPException):
    """Error al superar la cantidad limite de reenvios"""
    def __init__(self, message: str) -> None:
        super().__init__(message)


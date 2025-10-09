import socket 
from .config import *

def main() -> None:

    # Inicializar socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((SERVER_IP, SERVER_PORT))

    print("...Server UP...")

    try:
        # Esperar mensajes
        while True:
            msg, _ = s.recvfrom(BUFF_SIZE)

            # Imprimir mensajes en pantalla
            print(msg)
    except KeyboardInterrupt:
        print("...Server DOWN...")


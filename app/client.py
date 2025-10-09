import socket
from pathlib import Path
from .config import *

def main() -> None:

    # Inicializar socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("...Client UP...")

    while True:

        # Esperar input del usuario
        try:
            line = input().encode(encoding='utf-8')
        except EOFError:
            print("...Client DOWN..")
            break

        # Enviar input al servidor de a 16 bytes por vez
        sent = 0
        to_send = len(line)
        while sent < to_send:
        
            data = line[sent:sent+16]
            print(line[sent:sent+16])
            s.sendto(data, (SERVER_IP, SERVER_PORT))

            # Preparar próxima iteración
            sent += 16


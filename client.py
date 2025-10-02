import socket

# Definir tamaño máximo de mensajes
MAX_SIZE = 16

if __name__ == "__main__":
    # Obtener archivo desde entrada estándar
    file = input()

    # Crear socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enviar archivo por trozos
    to_send: int = len(file)
    sent: int = 0
    while sent < to_send:
        data: str = file[sent:sent+16]
        s.sendto(data.encode(), ("localhost", 5000))
        sent += 16


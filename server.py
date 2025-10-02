import socket

if __name__ == "__main__":
    # Crear socket UDP y configurarlo
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("localhost", 5000))

    # Recibir mensajes
    while True:
        data, _ = s.recvfrom(16)
        print(data)


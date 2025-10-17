from tcp.socket_tcp import SocketTCP

def main(address: tuple[str, int], buff_size: int, expected: int) -> None:

    # Inicializar socket
    server_socket = SocketTCP()

    # Dejar servidor eschando en la dirección deseada
    server_socket.bind(address)

    print("...Server UP...")

    # Aceptar conexión
    connection_socketTCP, _ = server_socket.accept()

    received_data = b""
    received_bytes = 0
    expected_bytes = expected
    while received_bytes < expected_bytes:
        received_data += connection_socketTCP.recv(buff_size)
        received_bytes = len(received_data)

    # Imprimir mensaje
    print(received_data.decode())

    # Esperar cierre de conexión
    server_socket.recv_close()

    print("...Server DOWN...")

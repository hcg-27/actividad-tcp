from tcp.socket_tcp import SocketTCP


def main(address: tuple[str, int], debug_enabled: bool = False):

    server_socketTCP = SocketTCP(debug_enabled)
    server_socketTCP.bind(address)

    print("SERVER STATUS: ON")

    if debug_enabled:
        print("========== MODO DEBUG ==========")
        print("MANEJANDO PERDIDAS: SI")

    connection_socketTCP, _ = server_socketTCP.accept()
    
    received_msg = connection_socketTCP.recv(21)

    # Mientras queden bytes por recibir
    while not connection_socketTCP.waiting_len:
        received_msg += connection_socketTCP.recv(21)

    print("\n" + received_msg.decode())
    
    connection_socketTCP.recv_close()
    
    print("\nSERVER STATUS: OFF")
    

from tcp.socket_tcp import SocketTCP


def main(address: tuple[str, int], debug_enabled: bool) -> None:

    print("CLIENT STATUS: ON")

    if debug_enabled:
        print("========== MODO DEBUG ==========")
        print("MANEJANDO PERDIDAS: SI")

    client_socketTCP = SocketTCP(debug_enabled)
    client_socketTCP.connect(address)
    
    message = b""
    while True:

        try:

            message += input().encode("utf-8")
        
        except EOFError:

            break

    client_socketTCP.send(message)
    

    client_socketTCP.close()
    print("CLIENT STATUS: OFF")
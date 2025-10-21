from tcp.socket_tcp import SocketTCP


def main(address: tuple[str, int], debug_enabled: bool) -> None:

    client_socketTCP = SocketTCP(debug_enabled)
    client_socketTCP.connect(address)

    print("CLIENT STATUS: ON")
    
    while True:

        try:

            # Leer archivo línea por línea
            line = input().encode(encoding='utf-8')

        # Hasta que se alcance el EOF
        except EOFError:

            break

        client_socketTCP.send(line)

    client_socketTCP.close()
    print("CLIENT STATUS: OFF")
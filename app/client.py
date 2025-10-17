from tcp.socket_tcp import SocketTCP

def main(address: tuple[str, int]) -> None:

    # Inicializar socket
    client_socketTCP = SocketTCP()
    
    # Conectar con servidor
    client_socketTCP.connect(address)

    print("...Client UP...")

    while True:

        # Esperar input del usuario
        try:

            line = input().encode(encoding='utf-8')
        
        except EOFError:
            
            print("...Client DOWN...")
            break

        # Enviar input al servidor
        client_socketTCP.send(line)
    
    # Cerrar conexión
    client_socketTCP.close()

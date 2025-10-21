from tcp.socket_tcp import SocketTCP


def main(address: tuple[str, int], debug_enabled: bool = False):

    server_socketTCP = SocketTCP(debug_enabled)
    server_socketTCP.bind(address)

    print("SERVER STATUS: ON")

    connection_socketTCP, _ = server_socketTCP.accept()
    
    while True:
        
        try: 

            data = connection_socketTCP.recv(21)
            print(data.decode())
        
        except KeyboardInterrupt:

            break
    

    connection_socketTCP.recv_close()
    
    print("\nSERVER STATUS: OFF")
    

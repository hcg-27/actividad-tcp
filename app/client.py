from tcp.socket_tcp import SocketTCP


def main(address: tuple[str, int], debug_enabled: bool):

    #s = SocketTCP()
    #s.connect((SERVER_IP, SERVER_PORT))
    #print(s)

    client_socketTCP = SocketTCP(debug_enabled)
    client_socketTCP.connect(address)
    print(client_socketTCP)
    # test 1
    message = "Mensje de len=16".encode()
    client_socketTCP.send(message)
    # test 2
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)
    # test 3
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)

    client_socketTCP.close()
    print(client_socketTCP)
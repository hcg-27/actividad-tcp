import argparse
from app import client, server
from app.config import SERVER_IP, SERVER_PORT


class Parser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument("mode", choices=["server", "client",],
                                 help="Selecciona modo de ejecución")

        self.parser.add_argument("-d", "--debug", action="store_true",
                                 help="Activa modo debug")
        
        address_help = "Dirección del servidor en formato IP:PUERTO"
        self.parser.add_argument("-a", "--address", nargs="?",
                                 default=f"{SERVER_IP}:{SERVER_PORT}",
                                 help=address_help)

    def parse_args(self) -> bool:
        self.args = self.parser.parse_args()
    
    @property
    def get_mode(self) -> str:
        return self.args.mode
    
    @property
    def debug_enabled(self) -> bool:
        return self.args.debug
    
    @property
    def get_address(self) -> tuple[str, int]:
        ip, port = self.args.address.split(":")

        return ip, int(port)
    
    

if __name__ == "__main__":

    parser = Parser()
    parser.parse_args()

    if parser.get_mode == "server":
        server.main(parser.get_address, parser.debug_enabled)
    elif parser.get_mode == "client":
        client.main(parser.get_address, parser.debug_enabled)
    else:
        exit(1)

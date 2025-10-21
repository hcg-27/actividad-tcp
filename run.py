import argparse
from app import client, server


class Parser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(add_help=False)

        self.parser.add_argument("mode", choices=["servidor", "cliente",],
                                 help="Selecciona modo de ejecución")
        
        self.parser.add_argument("address", type=str,
                                 help="Dirección del servidor")
        
        self.parser.add_argument("port", type=int,
                                 help="Puerto del servidor")
        
        self.parser.add_argument("-h", "--help",
                                 action="help",
                                 help="Muestra este mensaje y termina")

        self.parser.add_argument("-d", "--debug", action="store_true",
                                 help="Activa modo debug")

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
        addr = self.args.address
        port = self.args.port

        return addr, int(port)
    
    

if __name__ == "__main__":

    parser = Parser()
    parser.parse_args()

    if parser.get_mode == "servidor":
        server.main(parser.get_address, parser.debug_enabled)
    elif parser.get_mode == "cliente":
        client.main(parser.get_address, parser.debug_enabled)
    else:
        exit(1)

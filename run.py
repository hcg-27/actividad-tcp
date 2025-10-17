from argparse import ArgumentParser, Namespace
from app import server
from app import client
from app import config

class Parser:
    """
    Clase encargada de manejar los argumentos de línea de comandos para ejecutar
    la aplicación en modo 'server' o 'client'.

    Modos disponibles:
    - 'server': permite especificar una IP y puerto en formato IP:PUERTO, tamaño de buffer y cantidad esperada de bytes
                Si no se proporciona, se usan los valores por defecto definidos en config.py.
    - 'client': permite especificar IP y puerto del servidor al cual conectarse en formato IP:PUERTO.

    Atributos:
        mode (str): Modo de ejecución seleccionado ('server' o 'client').
        address (tuple): Tupla (ip, puerto), disponible en 'server' y 'client'.
        expected (int): Bytes que se esperan recibir, disponible en 'server'
        buffer (int): Tamaño del buffer, solo disponible en modo 'server'

    Métodos:
        parse_args(): Parsea los argumentos de línea de comandos.
    """

    def __init__(self) -> None:
        # Parser principal
        self.parser = ArgumentParser(
            add_help=False
        )

        # Añadir ayuda
        self.parser.add_argument(
            "-h",
            "--help",
            action="help",
            default="muestra este mensaje de ayuda y termina",
            help="muestra este mensaje de ayuda y termina"
        )

        # Añadir sub parsers por modo (servidor, cliente)
        self.subparsers = self.parser.add_subparsers(
            dest="mode", 
            required=True, 
            help="selecciona modo de ejecución"
        )

        # Configurar parser del servidor
        self.server_parser = self.subparsers.add_parser(
            "server",
            help="ejecuta el servidor",
            add_help=False
        )
        self.server_parser.add_argument(
            "-h",
            "--help",
            action="help",
            default="muestra este mensaje de ayuda y termina",
            help="muestra este mensaje de ayuda y termina"
        )
        self.server_parser.add_argument(
            "-a",
            "--address",
            type=str,
            default=f"{config.SERVER_IP}:{config.SERVER_PORT}",
            help="dirección del servidor en formato IP:PUERTO"
        )
        self.server_parser.add_argument(
            "-b",
            "--buffer",
            type=int,
            default=config.BUFF_SIZE,
            help="tamaño de buffer a usar en el servidor"
        )
        self.server_parser.add_argument(
            "-e",
            "--expected",
            type=int,
            default=config.EXPECTED_BYTES,
            help="cantidad de bytes que se esperan recibir"
        )

        # Configurar parser del cliente
        self.client_parser = self.subparsers.add_parser(
            "client",
            help="ejecuta el cliente",
            add_help=False
        )
        self.client_parser.add_argument(
            "-h",
            "--help",
            action="help",
            default="muestra este mensaje de ayuda y termina",
            help="muestra este mensaje de ayuda y termina"
        )
        self.client_parser.add_argument(
            "-a",
            "--address",
            type=str,
            default=f"{config.SERVER_IP}:{config.SERVER_PORT}",
            help="dirección del servidor en formato IP:PUERTO"
        )

        # Inicialmente no hay argumentos
        self.args = Namespace()
    
    def parse_args(self):
        self.args = self.parser.parse_args()
    
    @property
    def mode(self) -> str:
        return self.args.mode
    
    @property
    def address(self) -> tuple[str, int]:
        ip, port = self.args.address.split(":")
        return ip, int(port)
    
    @property
    def buffer(self) -> int:
        return self.args.buffer
    
    @property
    def expected(self) -> int:
        return self.args.expected


if __name__ == "__main__":

    # Crear parser
    parser = Parser()

    # Parserar argumentos
    parser.parse_args()

    if parser.mode == "server":
        server.main(parser.address, parser.buffer, parser.expected)
    else:
        client.main(parser.address)

from app import server
from app import client
import sys

if __name__ == "__main__":

    if sys.argv[1] == "server":
        server.main()
    else:
        client.main()

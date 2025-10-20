import sys
from app import client, server


if __name__ == "__main__":

    if sys.argv[1] == "server":
        server.main()
    else:
        client.main()

from app import server
from app import client
import sys

if __name__ == "__main__":

    if sys.argv[1] == "server":
        #subprocess.run(["python", "app/server.py", *sys.argv[2:]])
        server.main()
    else:
        #subprocess.run(["python", "app/client.py", *sys.argv[2:]])
        client.main()

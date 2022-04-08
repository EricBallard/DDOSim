import os, sys
import time
import threading
from scapy.all import *

# Add sibling folder to path, import util modules
sys.path.append(os.path.abspath("./src/utils"))
import cli, sockets


def test(host, hostport, srcport):
    # Init socket
    client = sockets.get(host, hostport, True, True)
    client.sock.bind(("0.0.0.0", srcport))

    if client.connect():
        print("Opened TCP on from port ", srcport)
        time.sleep(5)
        client.close()
    else:
        print("Failed!!! ", srcport)


# Main()
if __name__ == "__main__":
    # Parse CLI args
    args = cli.get_args()

    for i in range(500):
        threading.Thread(
            target=test, args=(args.ip, args.port, random.randint(1024, 65535))
        ).start()
        time.sleep(random.uniform(0.1, 0.9))

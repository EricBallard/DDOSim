import os, sys

# Add sibling folder to path, import util modules
sys.path.append(os.path.abspath('./src/utils'))
import cli, sockets

# Config
data = str.encode("PING")

# Main()
if __name__ == "__main__":
    # Parse CLI args
    args = cli.get_args()

    # Init socket
    client = sockets.get(args.ip, args.port, args.tcp)
    print("CLIENT=", client.sock)

    # Send to server
    # TCP requires handshake | UDP is 'connection-less'
    if not (
        {client.connect(5) if args.tcp else True}
        and client.send_data(client.sock, data, client.hostAddressPort)
    ):
        print("FAILED to ping server, is it online?")
    else:
        # Receive from server
        client.get_data(client.sock)

    # Stop
    client.close()

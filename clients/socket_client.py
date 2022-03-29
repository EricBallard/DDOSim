# Add parent folder to path
import os, sys

sys.path.insert(1, os.path.join(sys.path[0], ".."))

# Import from parent directory
import util, sockets

# Main()
if __name__ == "__main__":
    # Parse CLI args
    args = util.get_args()

    # Init socket
    client = sockets.get(args.ip, args.port, args.tcp)
    print("CLIENT=", client.sock)

    # Send to server
    # TCP requires handshake | UDP is 'connection-less'
    if not (
        {client.connect() if args.tcp else True}
        and client.send_data(client.sock, str.encode("PING"), client.hostAddressPort)
    ):
        print("FAILED to ping server, is it online?")
    else:
        # Receive from server
        client.get_data(client.sock)

    # Stop
    client.close()

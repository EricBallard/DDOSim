import sys
import socket
import threading
import keyboard
import argparse
import select

# hostAddr = "107.152.41.214"
response = str.encode("PONG")
bufferSize = 1024

hostAddr = "127.0.0.1"
hostPort = 25565

class ThreadedServer(object):
    def __init__(self, host, port, useTCP):
        # Create server socket
        # https://docs.python.org/3/library/socket.html
        self.isTCP = useTCP
        print(f"Starting {'TCP' if self.isTCP else 'UDP'} server...")
        #print(f"Host: {host} Port: {port}")

        if useTCP:
            self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        else:  # UDP
            self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Configure
        self.host = host
        self.port = port
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            # Bind to host - 5s timeout
            self.sock.settimeout(5)
            self.sock.bind((str(self.host), int(self.port)))
            self.sock.settimeout(0)
        except Exception as e:
            print("Failed Start Sever: ", e)
            self.sock = None

    def open(self):
        if self.isTCP:
             # Accepting incoming connections (TCP only)
            self.sock.listen(0)
            read_list = [self.sock]
            
        self.shouldPoll = True
        while self.shouldPoll:
            try:
                # UDP - fast, sessionless, blindly accepts data
                # TCP - handshake, linear, slower than udp

                if self.isTCP:
                    readable, writable, errored = select.select(read_list, [], [], 3)

                    for sock in readable:
                        if sock is self.sock:
                            client, address = self.sock.accept()
                            print("Connected: ", address)
                            threading.Thread(target=self.echoTCP(client, address)).start()
                else:
                    # Read incoming data
                    self.sock.settimeout(None)
                    data = self.sock.recvfrom(bufferSize)

                    if not data:
                        raise Exception("Bad Data:", data)

                    message = data[0]
                    address = data[1]

                    # Log adrress + data receieved
                    size = sys.getsizeof(message)
                    print(f"{address}=={size} bytes")

                    #  Attempt to reply to client, on separate thread
                    threading.Thread(target=self.echoUDP(address)).start()
            except Exception as e:
                # Stopping
                self.close()
                print(
                    f"Failed to accept {'client' if self.isTCP else 'data'} due to: {e}",
                )

        print("Server is OFFLINE!")

    def echoUDP(self, client):
        try:
            self.sock.settimeout(10)
            self.sock.sendto(response, client)
            print(f"{client} | Sent Response!")
        except Exception as e:
            print(f"{client} | Failed to respond to client due to: {e}")

    def echoTCP(self, client, address):
        keepAlive = True
        while keepAlive:
            try:
                # Wait up to 10s for data
                client.settimeout(10)
                data = client.recv(bufferSize)

                if data:
                    client.send(response)
                    print(f"{address} | Sent Response!")
                else:  # Bad Data
                    raise Exception("Bad Data: ", e)
            except Exception as e:
                # Disconnect
                print(f"{client} | Failed to respond to client due to: {e}")
                keepAlive = False
                client.close()

    def close(self):
        self.shouldPoll = False
        server.sock.shutdown(socket.SHUT_RDWR)
        server.sock.close()

def listenForKey():
    print("Press 'Q' to STOP..!")
    shouldListen = True
    
    while shouldListen:
        try:
            # Stop server/thread on key q
            if keyboard.is_pressed("q"):
                shouldListen = False
                stop()
        except:
            continue

def stop():
    print("Stopping...")

    if server is not None:
        server.close()

    server.sock = None
    print("STOPPED!")

# Main()
# Configure Socket Server UDP/TCP via CLI - UDP is set by default
# EX; python3 servers/socket_server.py [TCP/UDP]
if __name__ == "__main__":

    # Check for CLI args / Set defaults
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", help="Target address to bind", default="127.0.0.1")
    parser.add_argument("--port", help="Target port to bind", default="25565")
    parser.add_argument("--tcp", help="Set server to use TCP", default=False)
    args = parser.parse_args()

    # Attempt to start server
    server = ThreadedServer(args.ip, args.port, args.tcp)
    print("Started Server: ", server.sock)

    if server.sock is None:
        # Failed to start server - stop
        stop()
    else:
        # Server started successfully!
        threading.Thread(target=server.open).start()

        # Start keyboard listener on new thread
        threading.Thread(target=listenForKey).start()

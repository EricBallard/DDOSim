import threading
import socket
import sys

# Config
bufferSize = 1024
response = str.encode("PONG")

hostAddr = None


def get_host_addr():
    global hostAddr

    if not hostAddr:
        hostAddr = socket.gethostbyname(socket.gethostname())

    return hostAddr


# Modular class for TCP/UDP Server & Client
class get(object):
    def __init__(self, host, port, useTCP, silent):
        # Create server/client socket
        # https://docs.python.org/3/library/socket.html
        self.silent = silent
        self.isTCP = useTCP

        if not silent:
            print(f"Starting {'TCP' if self.isTCP else 'UDP'} socket...")
            print(f"Host: {host} Port: {port}")

        if useTCP:
            self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        else:  # UDP
            self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Configure
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.hostAddressPort = (str(host), int(port))
        # Client by default, bind() will set to Server
        self.isServer = False

    #### Socket Management ####
    def bind(self):
        # Identify self as server, triggers shutdown @ close
        self.shouldPoll = True
        self.isServer = True

        try:
            # Bind to host - 5s timeout
            self.sock.settimeout(3)
            self.sock.bind(self.hostAddressPort)
        except Exception as e:
            print("FAILED to start sever: ", e)
            self.sock = None

    def open(self):
        # Success, Poll....
        if self.isTCP:
            # Accepting incoming connections (TCP only)
            self.sock.listen(0)

        while self.shouldPoll:
            try:
                # UDP - fast, session-less
                # TCP - handshake, linear, slower than udp
                self.sock.settimeout(None)

                if self.isTCP:
                    # TCP -  Accept new client
                    client, address = self.sock.accept()

                    # Receive data from client on dedicated thread
                    threading.Thread(
                        target=self.handle_client, args=(client, address)
                    ).start()

                else:
                    # UDP -  Read incoming data
                    address, data = self.get_data(self.sock)

                    # Validate
                    if not address:
                        continue

                    #  Attempt to reply to client, on separate thread
                    threading.Thread(
                        target=self.send_data, args=(self.sock, response, address)
                    ).start()
            except Exception as e:
                # Stopping
                if self.shouldPoll:
                    print(
                        f"Failed to accept {'client' if self.isTCP else 'data'} due to: {e}",
                    )
                    self.close()

        print("Server is OFFLINE!")

    def connect(self, timeout):
        try:
            # Attempt to connect to host
            self.sock.settimeout(timeout)
            self.sock.connect(self.hostAddressPort)
            return True
        except Exception as e:
            if not self.silent:
                print("FAILED to connect: ", e)
            return False

    def close(self):
        # Close client socket
        print("Closing...")

        if self.isServer:
            self.shouldPoll = False
            # self.sock.shutdown(socket.SHUT_RDWR)

        self.sock.close()
        print("Disconnected!")

    #### Communication ####
    def send_data(self, socket, data, address):
        try:
            # Attempt to send data to server, 5s timeout
            socket.settimeout(5)

            if self.isTCP:
                # TCP - Socket should be client connection, address is unused
                socket.send(data)
            else:
                # UDP - Socket should be server socket itself
                socket.sendto(data, address)

            # Log adrress + data receieved
            size = sys.getsizeof(data)

            # Truncate data for logging
            data = str(data)
            data = (data[:75] + "..") if len(data) > 75 else data

            if not self.silent:
                print(f"{address} | @SENT ~ {size} bytes | {data}")
            return True
        except Exception as e:
            # Ignore error on server shutdown
            if not self.silent and (not self.isServer or self.shouldPoll):
                print(f"{address} | @FAILED to send data: {type(e)}")

        return False

    def get_data(self, conn):
        try:
            # Receieve data from server/client
            data = conn.recv(bufferSize) if self.isTCP else conn.recvfrom(bufferSize)

            if self.isTCP:
                address = get_host_addr()
            else:
                address = data[1]
                data = data[0]

            # Log adrress + data receieved
            size = sys.getsizeof(data)

            # Truncate data for logging
            log = (data[:75] + "..") if len(data) > 75 else data
            if not self.silent:
                print(f"{address} | @RECEIVED ~ {size} bytes | {log}")
        except Exception as e:
            # Ignore error on server shutdown
            # if not self.isServer or self.shouldPoll:
            if not self.silent:
                print(f"@FAILED to get data: {e}")
            address = None
            data = None

        # Returns sender address
        return (address, data)

    def handle_client(self, client, address):
        print(f"{address} | @CONNECTED")
        keepAlive = True

        while keepAlive and self.shouldPoll:
            try:
                # Wait up to 10s for data
                client.settimeout(10)
                addr, data = self.get_data(client)

                if data:
                    # Respond
                    self.send_data(client, response, address)

                    # Done
                    keepAlive = False
                else:  # Bad Data
                    raise Exception("RECEIVED NO/BAD DATA")
            except Exception as e:
                if self.shouldPoll:
                    # Disconnect
                    print(f"{address} | @DROPING ~ {e}")
                    keepAlive = False

        client.close()
        print(f"{address} | @CLOSED")

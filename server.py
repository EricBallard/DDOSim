import sys
import socket
import threading
import keyboard


hostAddr = "107.152.41.214"
#hostAddr = "127.0.0.1"
hostPort = 25565
bufferSize = 1024

# Cache
serverSocket = None
keyListener = None

# Functions
def startServer():
    print("Starting Server...")
    # Create UDP server socket
    # https://docs.python.org/3/library/socket.html
    serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind socket to host
    try:
        serverSocket.bind((hostAddr, hostPort))
        return serverSocket
    except Exception as e:
        print("Failed Start Sever: ", e)
        return None

def listenForKey():
    print("Press 'Q' to STOP..!")

    while True:
        try:
            # Stop server/thread on key press
            if keyboard.is_pressed("q"):
                stop()
                break
        except:
            break

def start():
    # Attempt to start server
    serverSocket = startServer()
    print("Started Server: ", serverSocket)

    # Failed to start server - stop
    if serverSocket is None:
        stop()
        return
    # Server started successfully!

    # Start keyboard listener on new thread
    keyListener = threading.Thread(target=listenForKey)
    keyListener.start()

    # Server poll
    while True:
        try:
            bytesAddressPair = serverSocket.recvfrom(bufferSize)

            message = bytesAddressPair[0]
            address = bytesAddressPair[1]
            size = sys.getsizeof(message)

            print(f"{address} {message} {size}")

            # Sending a reply to client
            serverSocket.sendto(str.encode("PONG"), address)
        except Exception as e:
            print("Failed to handle data data due to ", e)
            stop()
            break

def stop():
    if serverSocket is not None:
        serverSocket.close()

    print("Stopped...!")

# Main()
if __name__ == "__main__":
    start()

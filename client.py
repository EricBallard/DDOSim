import socket
#import socks

bytesToSend = str.encode("PING")
#serverAddressPort = (str("107.152.41.214"), int(25565))
serverAddressPort = (str("127.0.0.1"), int(25565))
bufferSize = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.settimeout(10)

#client = socks.socksocket()
#client.setproxy(socks.PROXY_TYPE_SOCKS5, "184.178.172.5")
#client.port = 15303
#client.connect(("107.152.41.214", 25565))

# Send to server using created UDP socket
UDPClientSocket.connect(serverAddressPort)
print('connected')

UDPClientSocket.send(bytesToSend)
#client.send(bytesToSend)
print('sent data')

msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msg = "Message from Server {}".format(msgFromServer[0])

print(msg)
print("sent")

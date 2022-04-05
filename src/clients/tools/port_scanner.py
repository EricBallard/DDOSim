from scapy.all import *
import socket

# Silence scapy debug
conf.verb = 0

ip = "107.152.41.214"
port = int(22)


def is_online():
    reply = sr1(IP(dst=ip, ttl=20) / ICMP(), timeout=2)
    return False if reply is None else True


def is_port_open(port):
    # Send SYN packet
    response = sr1(IP(dst=ip) / TCP(dport=port, flags="S"), timeout=2, verbose=0)

    try:
        # Check for response, if available check for ACK
        if response.getlayer(TCP).flags == "SA":
            return True
    except AttributeError:
        pass
    return False


# Main()
if __name__ == "__main__":
    print("Checking if host is online...")

    # Check if host is online
    for i in range(5):
        online = is_online()

        if online:
            break

    if online:
        print("Scanning ports...")
        open_ports = []

        # Scan ports, cache index if open
        for i in range(1, 100):
            if is_port_open(i):
                open_ports.append(i)

        # Print open ports with related service
        for port in open_ports:
            print ("OPEN: %s => %s" %(port, socket.getservbyport(port, "TCP"))) 
    else:
        print(f"Unable to ping host, is it online? ({ip})")
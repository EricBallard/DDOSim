from scapy.all import *

SYNACK_FLAG = 0x12
RSTACK_FLAG = 0x14

# Config
ports = range(int(1), int(100))


def is_online(ip):
    try:
        print("Pining... ", ip)
        ping = sr1(IP(dst=ip) / ICMP())
        print(ping)
        return True
    except Exception:
        return False


def scan(target, port):
    src_port = RandShort()
    
    print("Checking Port: ", port)
    response = sr(IP(dst=target) / TCP(sport=src_port, dport=port, flags="S"))
    # Extract flags of recived packet
    pktflags = response.getlayer(TCP).flags

    if pktflags == SYNACK_FLAG:
        RSTpkt = IP(dst=target) / TCP(sport=src_port, dport=port, flags="R")
        send(RSTpkt)

        print("Port is OPEN: ", port)
        return True
    else:
        return False


# Main()
if __name__ == "__main__":
    target = "107.152.41.214"
    
    # Start
   # if not is_online(target):
   #     print("@FAILED: Unable to to reach server, is it online?")
   # else:
    print("Scanning ports...")

    try:
        for port in ports:
            status = scan(target, port)
            if status == True:
                print("Port " + str(port) + ": Open")
    except KeyboardInterrupt:
        print("\n[*] User Requested Shutdown...")

from scapy.all import *

# Returns TCP flag in packet, if available
def get_flag(packet):
    if packet is None or not packet.haslayer(TCP):
        return None
    else:
        return packet.getlayer(TCP).flags


class session:

    # Constructor
    def __init__(self, host, port):
        self.ip = IP(dst=host)
        self.port = port
        self.sport = 1337

    # Returns Layer 4 (Transportation) Configured for TCP with parameters
    # https://packetlife.net/blog/2010/jun/7/understanding-tcp-sequence-acknowledgment-numbers/
    def get_protocol(self, flag, seq=None, ack=None):
        protocol = TCP(sport=self.sport, dport=self.port, flags=flag)

        if seq is not None:
            protocol.seq = seq
        if ack is not None:
            protocol.ack = ack

        return protocol

    # 3-way handshake
    def connect(self):
        # Init connection with Synchronization request
        # TODO: Random starting seq
        protocol = self.get_protocol("S", seq=1000)
        print("syn...")

        # NOTE: (SR = Send & Receive -> first answer )
        syn_req = sr1(self.ip / protocol, timeout=2, verbose=0)
        self.ack = syn_req.seq + 1
        self.seq = syn_req.ack

        # Check for response to request, process if available
        req_res = get_flag(syn_req)
        print("req_res: ", req_res)

        if req_res == "SA":
            # Acknowledge server's response
            send(self.ip / self.get_protocol("A", seq=self.seq, ack=self.ack))
            # NOTE: Handshake considered complete
            return True
        else:
            if req_res == "A":  # TODO
                # Check for half-open connection, reset if needed
                rst_req = self.get_protocol("FA")
                send(self.ip / rst_req)
            else:
                # No response/flags, port is closed?
                print("syn NOT ack!")

        return False

    # Apparently there's a handshake to close too..
    def close(self):
        print("closing...")
        # Send request to Finish connection, wait for reply
        protocol = self.get_protocol("FA", seq=self.seq, ack=self.ack)
        fin_req = sr1(self.ip / protocol, timeout=2, verbose=0)
        self.seq += 1

        # Check for response to request, process if available
        req_res = get_flag(fin_req)
        print("fin_res: ", req_res)

        if req_res == "FA":
            # Sever has acknowledged we are finished
            # (Let them know that we know that they know, seriously)
            send(self.ip / self.get_protocol("A", seq=self.seq, ack=self.ack))
            # NOTE: Disconnected, srcport # is now available for new connection on server
            print("CLOSED!")
            return True

        return False


""" # Inform server we're going to disconnect
FIN = TCP(sport=SOURCE_PORT, dport=80, flags="R", seq=ACK.ack, ack=SYNACK.seq + 1)
fin_req = sr1(ip / FIN, timeout=2, verbose=0)

print("FIN SEQ: ", FIN.seq)

try:
print("FLAGS: ", fin_req.getlayer(TCP).flags)
if not (fin_req.getlayer(TCP).flags == "A"):
    raise
except AttributeError:
print("FIN not ACK'd")
sys.exit(1)
 """

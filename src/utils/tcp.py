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
        self.sport = 6543
        self.seq = 0  # Bytes sent
        self.ack = 0  # Bytes recieved

    # Returns Layer 4 (Transportation) Configured for TCP with parameters
    # https://packetlife.net/blog/2010/jun/7/understanding-tcp-sequence-acknowledgment-numbers/
    def get_protocol(self, flag, seq=None, ack=None):
        protocol = TCP(sport=self.sport, dport=self.port, flags=flag)

        if seq is not None:
            protocol.seq = seq
        if ack is not None:
            protocol.ack = ack

        return protocol

    def connect(self):
        # Init connection with Synchronization request
        # TODO: Random starting seq
        protocol = self.get_protocol("S", seq=1000)
        print("syn...")

        # NOTE: (SR = Send & Receive -> first answer)
        syn_req = sr1(self.ip / protocol, timeout=2, verbose=0)

        if syn_req is None:
            return False

        # https://stackoverflow.com/questions/2352524/why-does-a-syn-or-fin-bit-in-a-tcp-segment-consume-a-byte-in-the-sequence-number
        # Increase sent bytes, sent SYN flag = phantom byte
        self.seq = syn_req.ack

        # Check for response to request, process if available
        req_res = get_flag(syn_req)
        print("req_res: ", req_res)

        if req_res == "SA":
            # Increase acknowledged bytes, recieved SYN flag = phantom byte
            self.ack = syn_req.seq + 1

            # Acknowledge server's response
            send(self.ip / self.get_protocol("A", seq=self.seq, ack=self.ack))
            # NOTE: Handshake considered complete
            return True
        else:
            if req_res == "A":  # TODO
                # Check for half-open connection, reset if needed
                rst_req = self.get_protocol("FA")
                send(self.ip / rst_req)
            # else: No response/flags, port is closed?

        return False

    def close(self):
        # Send request to Finish connection, wait for reply
        protocol = self.get_protocol("FA", seq=self.seq, ack=self.ack)
        fin_req = sr1(self.ip / protocol, timeout=2, verbose=0)

        # Increase sent bytes, sent FIN flag = phantom byte
        self.seq += 1

        # Check for response to request, process if available
        req_res = get_flag(fin_req)
        print("fin_res: ", req_res)

        if req_res == "FA":
            # Increase acknowledged bytes, recieved FIN flag = phantom byte
            self.ack = fin_req.seq + 1

            # Sever has acknowledged we are finished, acknowledge their reply
            send(self.ip / self.get_protocol("A", seq=self.seq, ack=self.ack))
            # NOTE: Disconnected, srcport # is now available for new connection on server
            return True

        return False

    def send(self, payload):
        # Init protocol, build packet
        protocol = self.get_protocol("PA", seq=self.seq, ack=self.ack)
        packet = self.ip / protocol / payload

        # Send packet, wait for reply
        psh_res = sr1(packet, timeout=2, verbose=0)

        # Check for response to request, process if available
        req_res = get_flag(psh_res)
        print("psh_res: ", req_res)

        if req_res == "A":
            # Server acknowledged byte recieved, adjust bytes sent
            self.seq = psh_res.ack
            return True

        return False

    def receive(self, to):
        # Query (sniff) for packets
        print("querying...")

        query = sniff(
            count=1,
            timeout=to,
            lfilter=lambda p: p.haslayer(IP)
            and p.haslayer(TCP)
            and p[TCP].payload is not None,
        )

        print("query completedf...")

        # Return info
        packet = query[0]

        if packet is None:
            return (None, None)
        else:
            # Increase # of bytes received
            self.ack = packet[TCP].seq + len(packet[Raw])

            # Acknowledge server we received data
            send(self.ip / self.get_protocol("A", seq=self.seq, ack=self.ack))

            # Return tuple  = flag, payload as string
            return (packet[TCP].flags, bytes(packet[TCP].payload).decode('UTF8','replace'))

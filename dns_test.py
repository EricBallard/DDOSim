# Imports
from scapy.all import *
from pprint import pprint
import operator

# Parameters
interface = "eth0"
src_mac = '00:00:00:00:00:00'

dns_source = "127.0.0.1"
dns_destination = ["8.8.8.8"]

time_to_live = 128
query_name = "google.com"
query_type = [
    "ANY",
    "A",
    "AAAA",
    "CNAME",
    "MX",
    "NS",
    "PTR",
    "CERT",
    "SRV",
    "TXT",
    "SOA",
]  # DNS Query Types

# Initialise variables
results = []
packet_number = 0

# Loop through all query types then all DNS servers
for i in range(0, len(query_type)):
    for j in range(0, len(dns_destination)):
        packet_number += 1

        # Sending the packet
        try:
            # Craft the DNS query packet with scapy
            packet = (
                Ether(src=src_mac)
                / IP(src=dns_source, dst=dns_destination[j], ttl=time_to_live)
                / UDP(sport=2118)
                / DNS(rd=1, qd=DNSQR(qname=query_name, qtype=query_type[i]))
            )

            query = sendp(packet, iface=interface, verbose=False)
            # query = sr1(packet, iface=interface, verbose=False, timeout=8)
            print("Packet #{} sent!".format(packet_number))
        except Exception as e:
            print("Error sending packet #{}".format(packet_number))
            print(e)
            # sys.exit(1)

        # Creating dictionary with received information
        try:
            result_dict = {
                "dns_destination": dns_destination[j],
                "query_type": query_type[i],
                "query_size": len(packet),
                "response_size": len(query),
                "amplification_factor": (len(query) / len(packet)),
                "packet_number": packet_number,
            }
            results.append(result_dict)
        except:
            pass

# Sort dictionary by the amplification factor
results.sort(key=operator.itemgetter("amplification_factor"), reverse=True)

# Print results
pprint(results)

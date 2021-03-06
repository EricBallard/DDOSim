# Exmple Half-Open scan, other viable types of stealth scanning; XMas Tree, FIN, Null

# NOTE: Windows
# Microsoft operating systems in addition to a number of others have
# ignored the RFC for TCP and have implemented it somewhat differently than the
# standard. This causes the FIN, Xmas tree, and Null scans to fail on Windows based
# operating systems, and others such as Cisco, HP/UX, and IRIX.

# https://www.giac.org/paper/gsec/1985/stealth-port-scanning-methods/103446

from socket import getservbyport
from scapy.all import *
import threading
import math
import time
import sys

# Add sibling folder to path, import util modules
sys.path.append(os.path.abspath("./src/utils"))
import cli, sockets


def is_online(host):
    reply = sr1(IP(dst=host, ttl=20) / ICMP(), timeout=2, verbose=0)
    return False if reply is None else True


def parse_version(info):
    info = str(info, "utf-8")
    return info


get_request = b"GET / HTTP/1.1\r\n\r\n"


def is_open(host, port):
    client = sockets.get(host, port, True, True)
    client.silent = True

    if client.connect(1):
        # If HTTP server, send GET request to extract info
        # Otherwise many services auto send info after handshake
        if port == 80 or port == 443:
            client.send_data(client.sock, get_request, client.hostAddressPort)

        address, data = client.get_data(client.sock)
        return data

    return None


def is_open_stealth(host, port):
    # Send SYN packet
    response = sr1(
        IP(dst=host) / TCP(dport=port, flags="S"), timeout=2, seq=100, verbose=0
    )

    try:
        # Check for response, if available check for SYN-ACK flag
        # Any other response the port is closed
        if response.getlayer(TCP).flags == "SA":
            return response
    except AttributeError:
        pass
    return None


def scan_range(host, fro, to):
    global results

    # NOTE: range(1-100) Will start @ index 1 and end @ index 99 - ??
    for i in range(fro, to):
        results["scanned_ports"] += 1
        # scan_result = is_open(host, i)
        scan_result = is_open_stealth(host, i)

        if scan_result is not None:
            # Half-Open scan superiorly faster than full 3way handshake
            # However, if port is open we'll need to complete the handshake
            # to send/recieve data in attempt to parse the service version
            # if scan_result is None:
            #    print("STEASLTH PASSED BUT 3WAY FAILED: ", i)
            #    pass

            # Acknowledge server response, completing tcp handshake
            conn_id = scan_result.seq + 1
            conn = sr1(
                IP(dst=host) / TCP(dport=port, flags="A"),
                seq=conn_id,
                ack=conn_id,
                timeout=2,
                verbose=0,
            )

            # Finialized hand shake.. send packet
            reply = sr1(
                IP(dst=host)
                / TCP(dport=i, flags="PA", seq=conn.seq + 1, ack=conn_id)
                / get_request,
                timeout=2,
            )
            
            print(reply)

            # Acknowledge server response, terminate connection
            # (Releases port, otherwise this would be a SYN flood attack)
            sr1(
                IP(dst=host) / TCP(dport=port, flags="F"),
                seq=(reply.seq + 1),
                ack=conn_id,
                timeout=2,
                verbose=0,
            )

            # Port is open - cache details
           # results["open_ports"].append(
            #    {
             #       "port": i,
             #       "service": str.upper(getservbyport(i, "TCP")).rjust(4),
             #       "version": parse_version(scan_result),
             #   }
            #)


# Main()
results = {"scanned_ports": 0, "open_ports": []}
toolbar_width = 40

if __name__ == "__main__":
    # Parse CLI args
    args = cli.get_args()

    # Init config
    start_port = int(args.start)
    end_port = int(args.end)
    total_ports = end_port - start_port

    # Validate input
    if total_ports < 1:
        print(f"@FAILED - Invalid Port Range: (Start: {start_port} End: {end_port})")
        sys.exit(1)

    start_time = time.time()
    print("@CHECKING if host is online...")

    # Check if host is online
    for i in range(5):
        online = True  # is_online(args.ip)

        if online:
            break

    if online:
        # Scan ports, cache index if open
        print(
            f"@SCANNING ports... ({start_port} - {end_port}) | THREADS: {args.threads}"
        )

        try:
            # Multi-Threaded scanner (Default 8)
            spawned_threads = []
            threads = int(args.threads)

            # Calculate # of ports to scan for each thread
            excess_load = total_ports % threads
            ports_per_thread = math.floor(total_ports / threads)

            # Start em up
            for t in range(threads):
                # Apply desired load for thread
                thread_load = (
                    ports_per_thread + excess_load
                    if t == threads - 1
                    else ports_per_thread
                )

                # Apply range of ports for thread
                thread_start_port = start_port if t == 0 else thread_end_port
                thread_end_port = thread_start_port + thread_load

                # SManage child thread
                child_thread = threading.Thread(
                    target=scan_range,
                    args=(args.ip, thread_start_port, thread_end_port),
                )

                spawned_threads.append(child_thread)
                child_thread.start()

            sys.stdout.write("[%s]" % (" " * toolbar_width))
            sys.stdout.flush()
            sys.stdout.write(
                "\b" * (toolbar_width + 1)
            )  # return to start of line, after '['

            for i in range(toolbar_width):
                time.sleep(0.1)  # do real work here
                # update the bar
                sys.stdout.write("-")
                sys.stdout.flush()

            sys.stdout.write("]\n")

            # Wait for child threads to finish
            for thread in spawned_threads:
                thread.join()

        except KeyboardInterrupt:
            # User interrupted
            print("@INTERRUPTED...")

        # Print stats
        run_time = time.time() - start_time
        print(
            f"Scanned {results['scanned_ports']} ports in {round(run_time, 2)}s | {args.ip}"
        )

        # Print results (pretty)
        keys = results["open_ports"]
        size = len(keys)

        #                str(keys[i]).capitalize().rjust(7),
        for i in range(size):
            result = keys[i]
            print(result["port"], " | ", result["service"], " | ", result["version"])
    else:
        print(f"@FAILED to ping host, is it online? | {args.ip}")

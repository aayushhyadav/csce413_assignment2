#!/usr/bin/env python3
"""
Port Scanner - Starter Template for Students
Assignment 2: Network Security

This is a STARTER TEMPLATE to help you get started.
You should expand and improve upon this basic implementation.

TODO for students:
1. Implement multi-threading for faster scans
2. Add banner grabbing to detect services
3. Add support for CIDR notation (e.g., 192.168.1.0/24)
4. Add different scan types (SYN scan, UDP scan, etc.)
5. Add output formatting (JSON, CSV, etc.)
6. Implement timeout and error handling
7. Add progress indicators
8. Add service fingerprinting
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import sys
import ipaddress
import json

def results_to_json(results):
    """
    Convert scan results into JSON-serializable format.
    """
    json_data = {}

    for host, ports in results.items():
        json_data[host] = {
            "open_ports": [
                {
                    "port": port,
                    "banner": banner
                }
                for port, banner in ports
            ]
        }

    return json_data

def expand_targets(target):
    """
    Expand a target into a list of IPs.
    Supports single IP/hostname or CIDR notation.
    """
    try:
        network = ipaddress.ip_network(target, strict=False)
        # Exclude network and broadcast addresses
        return [str(ip) for ip in network.hosts()]
    except ValueError:
        # Not a CIDR, treat as single host
        return [target]


def scan_port(target, port, timeout=2.0):
    """
    Scan a single port on the target host

    Args:
        target (str): IP address or hostname to scan
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds

    Returns:
        bool: True if port is open, False otherwise
    """
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        # Attempt connection
        result = sock.connect_ex((target, port))
        sock.close()

        # connect_ex returns 0 if successful
        if result == 0:
            banner = grab_banner(target, port)
            return True, banner

        return False, None

    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def grab_banner(target, port, timeout=2.0):
    """
    Attempt to grab a service banner from an open port

    Returns:
        str: Banner string or None
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((target, port))

        # HTTP-specific probe
        sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = sock.recv(1024)

        if banner:
            sock.close()
            return banner.decode(errors="ignore").strip()

    except (socket.timeout, OSError):
        pass

    return None

def scan_range(target, start_port, end_port, threads=10):
    """
    Scan a range of ports on the target host

    Args:
        target (str): IP address or hostname to scan
        start_port (int): Starting port number
        end_port (int): Ending port number

    Returns:
        list: List of open ports
    """
    open_ports = []

    print(f"[*] Scanning {target} from port {start_port} to {end_port}")
    print(f"[*] This may take a while...")
    print(f"[*] Using {threads} threads")

    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {
                executor.submit(scan_port, target, port): port
                for port in range(start_port, end_port + 1)
            }

            for future in as_completed(futures):
                port = futures[future]
                try:
                    is_open, banner = future.result()
                    if is_open:
                        print(f"[+] Port {port} is open")
                        if banner:
                            print(f"    Banner: {banner.splitlines()[0]}")
                        open_ports.append((port, banner))
                except Exception:
                    pass
    except Exception:
        print('Unexpected error occurred while scanning ', target)

    return open_ports

def parse_args():
    parser = argparse.ArgumentParser(description="Port Scanner")
    parser.add_argument(
        "--target", required=True,
        help="Target IP")

    parser.add_argument(
        "--ports",
        help="Ports to scan (Can be a single or multiple ports (8080 or 1-10000))",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--json",
        help="Write scan results to a JSON file"
    )

    return parser.parse_args()

def main():
    """Main function"""

    # arguments validation
    if len(sys.argv) < 2:
        print("Usage: python3 main.py --target <target> --ports <start_port>-<end_port> --threads <threads>")
        print("Example: python3 main.py --target 172.20.0.10 --ports 1-65535 --threads 100")
        sys.exit(1)

    args = parse_args()

    try:
        ports = args.ports.split('-') if args.ports else []
        start_port = int(ports[0]) if len(ports) > 0 else 1
        end_port = int(ports[1]) if len(ports) > 1 else start_port
        threads = args.threads
    except ValueError:
        print("Ports must be integers")
        sys.exit(1)

    if start_port < 1 or end_port > 65535 or (len(ports) == 2 and start_port > end_port):
        print("Invalid port range")
        sys.exit(1)

    targets = expand_targets(args.target)

    # Start scanning
    print(f"[*] Starting scan on {len(targets)} target(s)")

    results = {}

    for target in targets:
        print(f"\n[*] Scanning host: {target}")
        open_ports = scan_range(target, start_port, end_port, threads)
        results[target] = open_ports

    print("\n[+] Scan complete")

    # Print results
    for target, ports in results.items():
        print(f"\nHost: {target}")
        if ports:
            for port, banner in ports:
                print(f"    {port}/tcp")
                if banner:
                    print(f"        Banner: {banner.splitlines()[0]}")
        else:
            print("    No open ports found")

    # Save output in a JSON file
    if args.json:
        json_results = results_to_json(results)
        try:
            with open(args.json, "w") as f:
                json.dump(json_results, f, indent=4)
            print(f"\n[+] JSON results written to {args.json}")
        except OSError as e:
            print(f"[-] Failed to write JSON file: {e}")



if __name__ == "__main__":
    main()

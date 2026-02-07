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

from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import sys


def scan_port(target, port, timeout=10.0):
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
        # TODO: Create a socket
        # TODO: Set timeout
        # TODO: Try to connect to target:port
        # TODO: Close the socket
        # TODO: Return True if connection successful

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

def grab_banner(target, port, timeout=10.0):
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
        if port in (80, 8080, 8000, 443):
            sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")

        banner = sock.recv(1024)
        sock.close()

        if banner:
            return banner.decode(errors="ignore").strip()

    except (socket.timeout, OSError):
        pass

    return None

def scan_range(target, start_port, end_port, threads=100):
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

    # TODO: Implement the scanning logic
    # Hint: Loop through port range and call scan_port()
    # Hint: Consider using threading for better performance

    print(f"[*] Using {threads} threads")

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

    return open_ports


def main():
    """Main function"""
    # TODO: Parse command-line arguments
    # TODO: Validate inputs
    # TODO: Call scan_range()
    # TODO: Display results

    # Example usage (you should improve this):
    if len(sys.argv) < 2:
        print("Usage: python3 port_scanner_template.py <target> <start_port> <end_port> <threads>")
        print("Example: python3 port_scanner_template.py 172.20.0.10 1 65535 100")
        sys.exit(1)

    target = sys.argv[1]

    try:
        start_port = int(sys.argv[2]) if len(sys.argv) >= 3 else 1
        end_port = int(sys.argv[3]) if len(sys.argv) >= 4 else 1024
        threads = int(sys.argv[4]) if len(sys.argv) >= 5 else 100
    except ValueError:
        print("Ports must be integers")
        sys.exit(1)

    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print("Invalid port range")
        sys.exit(1)

    print(f"[*] Starting scan on {target}")

    open_ports = scan_range(target, start_port, end_port, threads)

    print("\n[+] Scan complete")
    if open_ports:
        print(f"[+] Open ports found ({len(open_ports)}):")
        for port, banner in open_ports:
            print(f"    {port}/tcp")
            if banner:
                print(f"        Banner: {banner.splitlines()[0]}")
    else:
        print("[-] No open ports found")


if __name__ == "__main__":
    main()

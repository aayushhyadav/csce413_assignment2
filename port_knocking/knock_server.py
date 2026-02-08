#!/usr/bin/env python3
"""Working port knocking server (TCP-based)."""

import argparse
import logging
import socket
import select
import time
import threading
import subprocess

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0
PROTECTED_TIMEOUT = 3600  # seconds


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def open_protected_port(container_ip, port):
    subprocess.run([
        "iptables", "-I", "INPUT",
        "-d", container_ip,
        "-p", "tcp",
        "--dport", str(port),
        "-j", "ACCEPT"
    ], check=False)

    logging.info("Firewall opened to %s:%d", container_ip, port)

def close_protected_port(container_ip, port):
    subprocess.run([
        "iptables", "-D", "INPUT",
        "-d", container_ip,
        "-p", "tcp",
        "--dport", str(port),
        "-j", "ACCEPT"
    ], check=False)

    logging.info("Firewall closed to %s:%d", container_ip, port)


class KnockTracker:
    def __init__(self, sequence, window):
        self.sequence = sequence
        self.window = window
        self.state = {}

    def process_knock(self, ip, port):
        now = time.time()

        if ip not in self.state:
            if port == self.sequence[0]:
                self.state[ip] = (1, now)
            return False

        index, start = self.state[ip]

        if now - start > self.window:
            del self.state[ip]
            return False

        if port == self.sequence[index]:
            index += 1
            if index == len(self.sequence):
                del self.state[ip]
                return True
            self.state[ip] = (index, start)
        else:
            del self.state[ip]

        return False

def listen_for_knocks(sequence, window, container_ip, protected_port):
    tracker = KnockTracker(sequence, window)
    sockets = []

    for port in sequence:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))
        s.listen(5)
        sockets.append(s)
        logging.info("Listening on knock port %d", port)

    while True:
        readable, _, _ = select.select(sockets, [], [])
        for s in readable:
            conn, addr = s.accept()
            ip = addr[0]
            port = s.getsockname()[1]
            conn.close()
            logging.info("Request detected from %s on port %d ", ip, port)

            if tracker.process_knock(ip, port):
                open_protected_port(container_ip, protected_port)
                threading.Timer(
                    PROTECTED_TIMEOUT,
                    close_protected_port,
                    args=(container_ip, protected_port),
                ).start()


def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking server")
    parser.add_argument(
        "--sequence",
        default=",".join(str(p) for p in DEFAULT_KNOCK_SEQUENCE),
    )
    parser.add_argument(
        "--target-ip", required=True,
        help="Docker container IP")

    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    sequence = [int(p) for p in args.sequence.split(",")]
    listen_for_knocks(sequence, args.window, args.target_ip, args.protected_port)


if __name__ == "__main__":
    main()

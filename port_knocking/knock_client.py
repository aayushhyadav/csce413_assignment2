#!/usr/bin/env python3
"""Working port knocking client."""

import argparse
import socket
import time

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_DELAY = 0.3


def send_knock(target, port, delay):
    try:
        with socket.create_connection((target, port), timeout=1):
            pass
    except OSError:
        pass
    time.sleep(delay)


def perform_knock_sequence(target, sequence, delay):
    for port in sequence:
        print(f"[+] Knocking on port {port}")
        send_knock(target, port, delay)


def check_protected_port(target, port):
    try:
        with socket.create_connection((target, port), timeout=5):
            print("[+] Protected service reachable:")
    except OSError:
        print("[-] Protected port is still closed")


def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking client")
    parser.add_argument("--target", required=True)
    parser.add_argument(
        "--sequence",
        default=",".join(str(p) for p in DEFAULT_KNOCK_SEQUENCE),
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    sequence = [int(p) for p in args.sequence.split(",")]

    perform_knock_sequence(args.target, sequence, args.delay)

    if args.check:
        check_protected_port(args.target, args.protected_port)


if __name__ == "__main__":
    main()

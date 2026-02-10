#!/usr/bin/env python3

import socket
import threading
import paramiko
import os
import logging

from logger import create_logger, log_connection
from ssh_server import FakeSSHServer

HOST_KEY_PATH = "/app/host_key"
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 22 

# generates RSA key-pair for the SSH server
def generate_host_key():
    if not os.path.exists(HOST_KEY_PATH):
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(HOST_KEY_PATH)

'''
# spawns a fake shell for every <channel, client> pair
# supports fake command responses for whoami, ls, uname -a, exit, logout
'''
def fake_shell(channel, client_ip):
    logger = logging.getLogger("Honeypot")

    channel.send("Welcome to Ubuntu 20.04.6 LTS\r\n")
    channel.send(f"Last login: Fri Feb 7 12:31:02 2026 from {client_ip}\r\n")
    channel.send("$ ")

    buffer = ""

    while True:
        try:
            data = channel.recv(1024)
            if not data:
                break

            char = data.decode("utf-8", errors="ignore")

            for c in char:
                # ENTER key
                if c in ("\r", "\n"):
                    command = buffer.strip()
                    buffer = ""

                    channel.send("\r\n")

                    if not command:
                        channel.send("$ ")
                        continue

                    logger.info(f"Command from {client_ip}: {command}")

                    if command in ("exit", "logout"):
                        channel.send("logout\r\n")
                        channel.close()
                        return

                    # Fake command responses
                    if command == "whoami":
                        channel.send("root\r\n")
                    elif command == "uname -a":
                        channel.send("Linux ubuntu 5.15.0-84-generic x86_64\r\n")
                    elif command == "ls":
                        channel.send(
                            "bin  boot  dev  etc  home  lib  root  tmp  usr  var\r\n"
                        )
                    else:
                        channel.send(f"{command}: command not found\r\n")

                    channel.send("$ ")

                # Backspace handling
                elif c == "\x7f":
                    if buffer:
                        buffer = buffer[:-1]
                        channel.send("\b \b")

                else:
                    buffer += c
                    channel.send(c)  # echo input

        except Exception as e:
            logger.error(f"Shell error from {client_ip}: {e}")
            break

    channel.close()

# creates a fake SSH server for every client
def handle_client(client, addr, host_key):
    logger = create_logger()
    client_ip, client_port = addr

    log_connection(client_ip, client_port)
    logger.info(f"New connection from {client_ip}:{client_port}")

    transport = paramiko.Transport(client)
    transport.add_server_key(host_key)

    server = FakeSSHServer(client_ip)

    try:
        transport.start_server(server=server)
        channel = transport.accept(20)

        if channel:
            fake_shell(channel, client_ip)

    except Exception as e:
        logger.error(f"SSH error from {client_ip}: {e}")
    finally:
        transport.close()


def run_honeypot():
    logger = create_logger()
    logger.info("SSH Honeypot starting")

    generate_host_key()
    host_key = paramiko.RSAKey(filename=HOST_KEY_PATH)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((LISTEN_HOST, LISTEN_PORT))
    sock.listen(100)

    logger.info(f"Listening on {LISTEN_HOST}:{LISTEN_PORT}")

    while True:
        client, addr = sock.accept()
        t = threading.Thread(
            target=handle_client,
            args=(client, addr, host_key),
            daemon=True,
        )
        t.start()


if __name__ == "__main__":
    run_honeypot()

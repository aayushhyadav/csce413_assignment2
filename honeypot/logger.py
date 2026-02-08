# logger.py
import json
import logging
import os
from datetime import datetime

LOG_DIR = "/app/logs"
HONEYPOT_LOG = os.path.join(LOG_DIR, "honeypot.log")
CONNECTIONS_LOG = os.path.join(LOG_DIR, "connections.jsonl")


def create_logger():
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("Honeypot")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(HONEYPOT_LOG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def log_connection(client_ip, client_port):
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "connection",
        "client_ip": client_ip,
        "client_port": client_port,
    }

    with open(CONNECTIONS_LOG, "a") as f:
        f.write(json.dumps(event) + "\n")

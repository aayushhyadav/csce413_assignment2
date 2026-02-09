FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends iptables iproute2 openssh-server \
    && rm -rf /var/lib/apt/lists/*

# Create the SSH run directory
RUN mkdir -p /var/run/sshd

# Create a user for SSH access
RUN useradd -m -s /bin/bash sshuser && \
    echo 'sshuser:SecurePass2024!' | chpasswd

COPY knock_server.py knock_client.py ./

# Expose SSH on port 2222 (non-standard port - students must discover this)
EXPOSE 2222

# Rejct any incoming packets to port 2222 to protect the SSH server
# Access is only granted after the client sends requests in the correct sequence
CMD ["/bin/sh", "-c", "\
    iptables -A INPUT -p tcp --dport 2222 -j REJECT --reject-with tcp-reset && \
    /usr/sbin/sshd -p 2222 && \
    python3 knock_server.py \
      --sequence 1234,5678,9012 \
      --target-ip 172.20.0.40 \
      --protected-port 2222 \
"]


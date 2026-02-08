FROM python:3.11-slim

WORKDIR /app

COPY main.py .

CMD ["python3", "main.py", "--target", "172.20.0.22", "--ports", "1-65535", "--threads", "100"]
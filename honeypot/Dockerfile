FROM python:3.11-slim

WORKDIR /app

COPY honeypot.py logger.py ssh_server.py requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 22

CMD ["python", "-u", "honeypot.py"]

FROM python:3.12-alpine

WORKDIR /app

# Install Docker CLI to run scraper container
RUN apk add --no-cache docker-cli

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scheduler.py .

# Expose API port
EXPOSE 8001

CMD ["python", "scheduler.py"]

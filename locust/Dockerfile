FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY locustfile.py .

# 8089 – web UI, 5557/5558 – master–worker kommunikáció
EXPOSE 8089 5557 5558

ENTRYPOINT ["locust"]

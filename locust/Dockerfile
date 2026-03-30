# Locust Dockerfile for OpenShift
# ==============================================================================
# This Dockerfile builds a Locust image for load testing.
# ==============================================================================

FROM registry.access.redhat.com/ubi9/python-39

WORKDIR /app

# Create a non-root user for security
RUN useradd -u 1000 -m -s /bin/bash locustuser && \
    mkdir -p /home/locustuser/.cache/pip && \
    chown -R locustuser:locustuser /app /home/locustuser/.cache

# Install dependencies as root first, then switch to non-root user
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY locustfile.py .

# Switch to non-root user
USER locustuser

# 8089 – web UI, 5557/5558 – master–worker kommunikáció
EXPOSE 8089 5557 5558

ENTRYPOINT ["locust"]

# Locust Dockerfile for OpenShift
# ==============================================================================
# This Dockerfile builds a Locust image for load testing.
# ==============================================================================

FROM registry.access.redhat.com/ubi9/python-39

WORKDIR /app

# OpenShift runs containers with an arbitrary non-root UID.
# Group-writable permissions for GID 0 keep the image SCC-compatible.
RUN mkdir -p /app && \
    chgrp -R 0 /app && \
    chmod -R g=u /app

# Install dependencies as root first, then switch to non-root user
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY locustfile.py .

# 8089 – web UI, 5557/5558 – master–worker kommunikáció
EXPOSE 8089 5557 5558

ENTRYPOINT ["locust"]

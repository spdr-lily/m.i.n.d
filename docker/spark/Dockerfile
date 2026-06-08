FROM bitnami/spark:3.5.0

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

USER 1001

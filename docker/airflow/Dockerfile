FROM apache/airflow:2.8.0-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt /requirements-prod.txt
RUN pip install --no-cache-dir -r /requirements-prod.txt

COPY . /app
ENV PYTHONPATH=/app

USER airflow

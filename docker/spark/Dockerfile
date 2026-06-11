FROM apache/spark:3.5.0

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-spark.txt /requirements-spark.txt
# Spark ships Python 3.8 which is incompatible with modern scipy/pandas
RUN pip install --no-cache-dir -r /requirements-spark.txt

COPY . /app
ENV PYTHONPATH=/app

USER spark

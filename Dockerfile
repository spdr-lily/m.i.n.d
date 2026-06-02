FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY mind-ui/package.json mind-ui/package-lock.json ./
RUN npm ci
COPY mind-ui/ .
RUN npm run build

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements-prod.txt

COPY . .
COPY --from=frontend-build /app/dist mind-ui/dist

RUN chmod +x entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; import os; port = os.environ.get('PORT', '8000'); urllib.request.urlopen(f'http://localhost:{port}/health')"

CMD ["./entrypoint.sh"]
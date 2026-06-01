#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting M.I.N.D API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

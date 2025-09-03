#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head

echo "Seeding admin..."
python seeder/seed_admin.py || true

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

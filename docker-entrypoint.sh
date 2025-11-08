#!/bin/bash
set -e

# Wait for PostgreSQL to become available
host="${POSTGRES_HOST:-localhost}"
port="${POSTGRES_PORT:-5432}"

echo "Waiting for database ${host}:${port} ..."
for i in {1..30}; do
  if nc -z "$host" "$port"; then
    echo "Database is up"
    break
  fi
  echo "Waiting... ($i)"
  sleep 2
done

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Seed database (idempotent)
echo "Seeding database..."
python seed_db.py || echo "Seed failed or already done"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn ShippingService.wsgi:application --bind 0.0.0.0:8004 --workers 3


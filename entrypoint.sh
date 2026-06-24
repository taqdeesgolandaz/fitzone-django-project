#!/usr/bin/env bash
set -euo pipefail

# Wait for database if needed (simple loop could be added here)

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn fitzone.wsgi:application --bind 0.0.0.0:${PORT:-8000}

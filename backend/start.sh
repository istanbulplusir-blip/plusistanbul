#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
while ! python manage.py check --database default 2>&1; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=peykan.settings_production

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn peykan.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 
#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
max_attempts=30
attempt=1

while ! python manage.py check --database default 2>&1; do
  if [ $attempt -ge $max_attempts ]; then
    echo "Database connection failed after $max_attempts attempts"
    exit 1
  fi
  echo "Database is unavailable - sleeping (attempt $attempt/$max_attempts)"
  sleep 2
  attempt=$((attempt + 1))
done

echo "Database is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
max_attempts=30
attempt=1

while ! python -c "import redis; r = redis.Redis.from_url('$REDIS_URL'); r.ping()" 2>/dev/null; do
  if [ $attempt -ge $max_attempts ]; then
    echo "Redis connection failed after $max_attempts attempts"
    exit 1
  fi
  echo "Redis is unavailable - sleeping (attempt $attempt/$max_attempts)"
  sleep 2
  attempt=$((attempt + 1))
done

echo "Redis is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=peykan.settings_production

# Create superuser if it doesn't exist (for initial setup)
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one manually.')
else:
    print('Superuser exists.')
"

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
    --keep-alive 2 \
    --access-logfile - \
    --error-logfile - \
    --log-level info 
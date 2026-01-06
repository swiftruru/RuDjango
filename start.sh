#!/bin/bash
set -e

# Activate virtual environment
. /app/.venv/bin/activate

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if not exists
echo "Creating superuser if not exists..."
python manage.py create_superuser

# Start Daphne server
echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p ${PORT:-8000} RuDjangoProject.asgi:application

#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear -v 2

echo "Listing collected static files..."
ls -la staticfiles/ || echo "staticfiles directory not found"
ls -la staticfiles/css/ || echo "staticfiles/css directory not found"

echo "Running migrations..."
python manage.py migrate

echo "Build completed successfully!"

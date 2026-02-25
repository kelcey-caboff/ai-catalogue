#!/bin/sh
set -e

echo "Collecting static files..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"

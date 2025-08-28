#!/bin/bash

set -e  # Exit on error

# Wait for the database to be ready (simple retry loop; adjust timeout as needed)
until python manage.py migrate --check; do
  echo "Waiting for database..."
  sleep 2
done

# Run migrations (safe to run idempotently)
python manage.py migrate

# Collect static files (runs every startup to handle any changes in development)
python manage.py collectstatic --noinput

# Load your fixtures using the custom management command
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures
python manage.py loadfixtures

# Start the ASGI server (exec passes control to the CMD or docker-compose command)
exec "$@"
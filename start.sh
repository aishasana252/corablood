#!/usr/bin/env bash
# Apply database migrations
python manage.py migrate

# Create default superusers if they don't exist
python create_superuser.py

# Start Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}

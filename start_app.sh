#!/bin/sh
set -e

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
echo "Starting server"
exec uvicorn vidoso.asgi:application --host 0.0.0.0 --port 8000 --reload

#!/bin/sh

echo "▶ Applying database migrations..."
python manage.py migrate || exit 1

echo "▶ Collecting static files..."
python manage.py collectstatic --noinput

echo "▶ Creating user roles..."
python manage.py init_roles || echo "⚠ Could not create roles"

echo "▶ Starting server..."
exec uvicorn game_management.asgi:application --host 0.0.0.0 --port 8000

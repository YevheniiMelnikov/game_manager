#!/usr/bin/env sh
set -e

if [ "${RUN_MIGRATIONS}" = "true" ]; then
  echo "▶ Applying database migrations..."
  python manage.py migrate --noinput

  echo "▶ Collecting static files..."
  python manage.py collectstatic --noinput

  echo "▶ Creating user roles..."
  python manage.py init_roles || echo "Could not create roles"
fi

echo "▶ Starting: $*"
exec "$@"

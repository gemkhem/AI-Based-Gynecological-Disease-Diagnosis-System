#!/usr/bin/env bash
set -e

# Ensure PYTHONPATH contains fron-end directory
export PYTHONPATH="/app/fron-end:${PYTHONPATH}"

echo "==> Running database migrations..."
python manage.py migrate --noinput

APP_PORT="${PORT:-8000}"
echo "==> Starting GDDES application server on port ${APP_PORT}..."

if [ "$1" = "gunicorn" ]; then
    shift
    exec gunicorn --bind "0.0.0.0:${APP_PORT}" --workers 3 --timeout 120 gddes.wsgi:application "$@"
fi

exec "$@"

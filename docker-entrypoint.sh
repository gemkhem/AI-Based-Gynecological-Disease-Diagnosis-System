#!/usr/bin/env bash
set -e

# Ensure PYTHONPATH contains fron-end directory
export PYTHONPATH="/app/fron-end:${PYTHONPATH}"

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Starting GDDES application server..."
exec "$@"

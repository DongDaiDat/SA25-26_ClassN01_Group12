#!/usr/bin/env sh
set -e

echo "[notification] Running migrations..."
python manage.py migrate --noinput

echo "[notification] Starting server..."
exec "$@"

#!/usr/bin/env bash
set -euo pipefail

echo "=== Build script start ==="

# Ensure python prints errors immediately
export PYTHONUNBUFFERED=1

# Install any build-time requirements if needed is handled by Render.
# Run migrations and collectstatic to prepare the app for production.
echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "=== Build script complete ==="

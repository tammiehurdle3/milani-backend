#!/usr/bin/env bash
# exit on error
set -o errexit

# Install modules
pip install -r requirements.txt

# Collect static files (CSS for Admin panel)
python manage.py collectstatic --no-input

# Update Database structure
python manage.py migrate
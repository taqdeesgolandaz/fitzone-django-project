#!/bin/bash
set -e

# Render database import helper
# Usage:
#   ./render_db_load.sh
# This loads render_data.json into the active Django database.

if [ ! -f render_data.json ]; then
  echo "Error: render_data.json not found. Run ./render_db_sync.sh first."
  exit 1
fi

echo "Loading render_data.json into the database..."
python manage.py loaddata render_data.json

echo "Done: render_data.json loaded."

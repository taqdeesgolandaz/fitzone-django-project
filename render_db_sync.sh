#!/bin/bash
set -e

# Render database export helper
# Usage:
#   ./render_db_sync.sh
# This creates a fixture file for importing into Render's PostgreSQL database.

echo "Exporting local database to render_data.json..."
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude migrations \
    --exclude sessions \
    --exclude admin.logentry \
    --indent 2 \
    > render_data.json

echo "Done: render_data.json created."
echo "Next steps:"
echo " 1. Add render_data.json to your repo or upload it to your Render instance."
echo " 2. In Render shell or after deployment, run: python manage.py loaddata render_data.json"
echo " 3. Verify admin and app data on Render after the load."

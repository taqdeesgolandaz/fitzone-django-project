#!/bin/bash
# Exit on error
set -o errexit

echo "🚀 Installing setuptools and wheel first..."
pip install --upgrade pip setuptools wheel

echo "📦 Installing all requirements from requirements.txt..."
pip install -r requirements.txt

echo "🔍 Verifying pkg_resources is available..."
python -c "import pkg_resources; print('✅ pkg_resources is available')"

echo "🔄 Running database migrations..."
python manage.py migrate

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"

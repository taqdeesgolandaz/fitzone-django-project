#!/bin/bash
# Exit on error
set -o errexit

echo "========================================="
echo "🚀 PHASE 1: Verifying Python and pip environment..."
echo "========================================="
python --version
python -m pip --version

echo "========================================="
echo "🚀 PHASE 2: Installing setuptools and wheel first..."
echo "========================================="
python -m pip install --upgrade pip setuptools wheel

echo "========================================="
echo "📦 PHASE 3: Installing requirements..."
echo "========================================="
python -m pip install --upgrade pip setuptools wheel
# Install psycopg2-binary early to ensure the PostgreSQL adapter is available
python -m pip install psycopg2-binary>=2.9.0 || true
python -m pip install -r requirements.txt

echo "========================================="
echo "🔍 PHASE 4: Verifying pkg_resources and razorpay..."
echo "========================================="
python -c "import pkg_resources; print('✅ pkg_resources available')"
python -c "import razorpay; print('✅ razorpay available')"

echo "========================================="
echo "🔄 PHASE 5: Running migrations..."
echo "========================================="
python manage.py migrate --noinput

echo "========================================="
echo "📁 PHASE 6: Collecting static files..."
echo "========================================="
python manage.py collectstatic --noinput

echo "========================================="
echo "✅ BUILD COMPLETE!"
echo "========================================="

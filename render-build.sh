#!/bin/bash
# Exit on error
set -o errexit

echo "========================================="
echo "🚀 PHASE 1: Installing setuptools first..."
echo "========================================="
pip install --upgrade pip setuptools wheel

echo "========================================="
echo "📦 PHASE 2: Installing requirements..."
echo "========================================="
pip install -r requirements.txt

echo "========================================="
echo "🔍 PHASE 3: Verifying pkg_resources..."
echo "========================================="
python -c "import pkg_resources; print('✅ pkg_resources available')"
python -c "import razorpay; print('✅ razorpay available')"

echo "========================================="
echo "🔄 PHASE 4: Running migrations..."
echo "========================================="
python manage.py migrate --noinput

echo "========================================="
echo "📁 PHASE 5: Collecting static files..."
echo "========================================="
python manage.py collectstatic --noinput

echo "========================================="
echo "✅ BUILD COMPLETE!"
echo "========================================="

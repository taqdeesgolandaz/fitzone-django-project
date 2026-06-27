#!/bin/bash
# render-build.sh

echo "========================================="
echo "🚀 Installing setuptools and wheel first..."
echo "========================================="
pip install --upgrade pip setuptools wheel

echo "========================================="
echo "📦 Installing all requirements..."
echo "========================================="
pip install -r requirements.txt

echo "========================================="
echo "🔍 Verifying razorpay installation..."
echo "========================================="
python -c "import pkg_resources; import razorpay; print('✅ Razorpay available')" || echo "❌ Razorpay verification failed"

echo "========================================="
echo "🔄 Running migrations..."
echo "========================================="
python manage.py migrate --noinput

echo "========================================="
echo "📁 Collecting static files..."
echo "========================================="
python manage.py collectstatic --noinput

echo "========================================="
echo "✅ Build complete!"
echo "========================================="

"""Check required packages for the Django app."""
import os
import sys
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')

try:
    import django
    print('django installed')
except Exception as exc:
    print('django import failed:', exc)

try:
    import pkg_resources
    print('pkg_resources installed')
except Exception as exc:
    print('pkg_resources import failed:', exc)

try:
    import razorpay
    print('razorpay installed')
except Exception as exc:
    print('razorpay import failed:', exc)

try:
    import cloudinary
    print('cloudinary installed')
except Exception as exc:
    print('cloudinary import failed:', exc)

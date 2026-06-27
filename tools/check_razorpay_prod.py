"""Run a production-style check of Razorpay package availability and key loading."""
import os
import sys
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')

try:
    import django
    django.setup()
    print('Django setup successful.')
except Exception as exc:
    print('Django setup failed:', type(exc).__name__, exc)
    raise

from django.conf import settings
print('RAZORPAY_KEY_ID=', settings.RAZORPAY_KEY_ID)
print('RAZORPAY_KEY_SECRET set=', bool(settings.RAZORPAY_KEY_SECRET))

try:
    import razorpay
    print('razorpay import OK')
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    print('client created OK')
except Exception as exc:
    print('razorpay check failed:', type(exc).__name__, exc)
    raise

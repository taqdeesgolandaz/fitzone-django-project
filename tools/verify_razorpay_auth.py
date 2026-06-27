"""Verify Razorpay API credentials from Django settings by creating a test order."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')
import django
django.setup()
from django.conf import settings

print('RAZORPAY_KEY_ID:', settings.RAZORPAY_KEY_ID)
print('RAZORPAY_KEY_SECRET present:', bool(settings.RAZORPAY_KEY_SECRET))

try:
    import razorpay
except ImportError as exc:
    raise SystemExit(f'Razorpay package not installed: {exc}')

if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
    raise SystemExit('Missing Razorpay credentials in settings.')

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
print('Client created successfully.')

order_data = {
    'amount': 100,
    'currency': 'INR',
    'receipt': 'verify_razorpay_auth_test',
    'payment_capture': 1,
}

try:
    order = client.order.create(data=order_data)
    print('Order created:', order)
except Exception as exc:
    print('Order creation failed:', type(exc).__name__, exc)
    if 'Authentication' in str(exc) or 'auth' in str(exc).lower():
        print('Authentication failed: verify the keys exactly and ensure they are active in Razorpay.')
    raise

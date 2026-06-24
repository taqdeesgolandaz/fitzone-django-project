import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')
import django
django.setup()

from notifications.email_templates import get_account_deleted_email
from accounts.models import CustomUser

u = CustomUser.objects.first()
html, _ = get_account_deleted_email(u)

if 'class="button"' in html:
    print('✓ FIXED! Account-deleted email now uses the simple button class')
    print('✓ Button should now be clickable like account-deactivated')
else:
    print('✗ ERROR: Button class not found')

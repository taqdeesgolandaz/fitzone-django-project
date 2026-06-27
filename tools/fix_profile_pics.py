"""
Run this script from the project root to fix existing `profile_picture` paths
that contain duplicated `profile_pics/profile_pics/...` entries.

Usage:
    python tools/fix_profile_pics.py

This will modify the database; ensure you have a backup.
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')
import django
django.setup()
from django.db import transaction
from accounts.models import CustomUser

fixed = 0
with transaction.atomic():
    for u in CustomUser.objects.exclude(profile_picture__isnull=True).exclude(profile_picture__exact=''):
        name = u.profile_picture.name
        if 'profile_pics/profile_pics/' in name:
            new_name = name.replace('profile_pics/profile_pics/', 'profile_pics/')
            print(f'Fixing user {u.id}: {name} -> {new_name}')
            u.profile_picture.name = new_name
            u.save(update_fields=['profile_picture'])
            fixed += 1
print(f'Done. Fixed {fixed} users.')

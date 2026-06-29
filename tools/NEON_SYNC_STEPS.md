# Neon Database Sync Guide

This file documents the correct steps to sync local Django data from `db.sqlite3` to the Neon/Postgres production database.

Use these steps whenever you make changes in the local environment and want to import them into Neon safely.

## Prerequisites

- Your local branch is clean or only contains intended changes.
- Local migrations are applied and your local data is correct.
- The Neon/Postgres connection URL is available.
- Your virtual environment is active or you know the path to `myenv\Scripts\python.exe`.

## Recommended Workflow

### 1. Verify local data before syncing

From the project root:

```powershell
cd C:\Users\GLOBAL T\Desktop\FitZone
myenv\Scripts\python.exe manage.py showmigrations
```

Check your local membership counts if needed:

```powershell
myenv\Scripts\python.exe - <<'PY'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')
import django
django.setup()
from django.apps import apps
from django.db.models import Count
Membership = apps.get_model('membership', 'UserMembership')
print('local memberships', Membership.objects.using('default').count())
print('local active memberships', Membership.objects.using('default').filter(status='active').count())
print('local membership by user:')
for row in Membership.objects.using('default').values('user__email').annotate(cnt=Count('id')).order_by('-cnt'):
    print(row)
PY
```

> Only sync after you confirm the local data is correct.

### 2. Set the Neon database URL

Use either `NEON_DATABASE_URL` or pass the value explicitly with `--RemoteUrl`.

Example:

```powershell
$env:NEON_DATABASE_URL = "postgresql://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require&channel_binding=require"
```

### 3. Do a dry run first

This shows the difference between local and remote without making changes.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync_neon.ps1 -RemoteUrl "$env:NEON_DATABASE_URL" -DryRun
```

Or:

```powershell
myenv\Scripts\python.exe manage.py sync_neon --remote-url "$env:NEON_DATABASE_URL" --dry-run
```

### 4. Review the dry-run report

- Confirm model counts are expected.
- Confirm there are no unexpected missing records on remote.
- If the remote already has incorrect duplicates, do not import yet.

### 5. Import the correct local records

If the dry-run looks correct, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync_neon.ps1 -RemoteUrl "$env:NEON_DATABASE_URL" -Import
```

Or:

```powershell
myenv\Scripts\python.exe manage.py sync_neon --remote-url "$env:NEON_DATABASE_URL" --import
```

### 6. Verify the Neon database after import

Re-run the verification query or use the Django admin dashboard:

```powershell
myenv\Scripts\python.exe - <<'PY'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')
import django
django.setup()
from django.conf import settings
import dj_database_url
from django.db import connections
from django.apps import apps
remote_url = os.getenv('NEON_DATABASE_URL')
remote_db = dj_database_url.config(default=remote_url, conn_max_age=600, conn_health_checks=True)
remote_db['ENGINE'] = remote_db.get('ENGINE','django.db.backends.postgresql')
remote_db['TIME_ZONE'] = getattr(settings, 'TIME_ZONE', 'UTC')
remote_db['AUTOCOMMIT'] = True
settings.DATABASES['remote_neon'] = remote_db
connections.databases['remote_neon'] = settings.DATABASES['remote_neon']
connections['remote_neon'].connect()
Membership = apps.get_model('membership', 'UserMembership')
print('remote memberships', Membership.objects.using('remote_neon').count())
print('remote active memberships', Membership.objects.using('remote_neon').filter(status='active').count())
PY
```

## Optional: Export local data instead of direct import

If you want to export local data as JSON first:

```powershell
myenv\Scripts\python.exe manage.py sync_neon --export-file local_neon_export.json
```

Then import later using a custom script or one-off management command.

## Handling bad remote data

If remote Neon already contains incorrect duplicates or stale rows, remove those bad records before importing.

### Safe cleanup approach

1. Use `--dry-run` to identify bad records.
2. If you need to delete all remote membership records and re-import only your trusted local rows:

```powershell
myenv\Scripts\python.exe - <<'PY'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')
import django
django.setup()
from django.conf import settings
import dj_database_url
from django.db import connections
from django.apps import apps
remote_url = os.getenv('NEON_DATABASE_URL')
remote_db = dj_database_url.config(default=remote_url, conn_max_age=600, conn_health_checks=True)
remote_db['ENGINE'] = remote_db.get('ENGINE','django.db.backends.postgresql')
remote_db['TIME_ZONE'] = getattr(settings, 'TIME_ZONE', 'UTC')
remote_db['AUTOCOMMIT'] = True
settings.DATABASES['remote_neon'] = remote_db
connections.databases['remote_neon'] = settings.DATABASES['remote_neon']
connections['remote_neon'].connect()
Membership = apps.get_model('membership', 'UserMembership')
Membership.objects.using('remote_neon').all().delete()
print('Deleted remote membership rows')
PY
```

3. Re-run the import step after cleanup.

## Notes

- Do not import if local data is not final or still under test.
- For production sync, always use `--dry-run` first.
- This repo’s sync command already compares `accounts.CustomUser`, `membership.MembershipPlan`, and `membership.UserMembership`.
- If you add new models to sync later, update `accounts/management/commands/sync_neon.py` accordingly.

## Quick command summary

```powershell
$env:NEON_DATABASE_URL = "postgresql://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require&channel_binding=require"

powershell -ExecutionPolicy Bypass -File .\tools\sync_neon.ps1 -RemoteUrl "$env:NEON_DATABASE_URL" -DryRun
powershell -ExecutionPolicy Bypass -File .\tools\sync_neon.ps1 -RemoteUrl "$env:NEON_DATABASE_URL" -Import
```

Or use the direct Python command:

```powershell
myenv\Scripts\python.exe manage.py sync_neon --remote-url "$env:NEON_DATABASE_URL" --dry-run
myenv\Scripts\python.exe manage.py sync_neon --remote-url "$env:NEON_DATABASE_URL" --import
```

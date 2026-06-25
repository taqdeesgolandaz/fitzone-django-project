# PythonAnywhere Deployment Guide

This Django app has been updated for PythonAnywhere deployment. The following instructions explain how to run it on PythonAnywhere.

## 1. Prepare the repository

- Ensure the repo contains the latest working code.
- Keep `db.sqlite3` in the repo if you want local data preserved; otherwise, remove it from version control and use a separate database for production.
- Add a `.env` or environment variables to PythonAnywhere for secrets.

## 2. Required files

- `manage.py`
- `fitzone/wsgi.py`
- `requirements.txt`
- `db.sqlite3` (optional for development only)

## 3. PythonAnywhere setup

1. Sign in to PythonAnywhere.
2. Create a new web app.
3. Choose Python version matching this project (e.g. 3.11).
4. Set the source code folder to the repository clone location.
5. Set the virtualenv path if using one.

## 4. Configure the web app

- In the "WSGI configuration file" section, ensure the WSGI file points to `fitzone.wsgi.application`.
- Example `WSGI configuration` snippet:

```python
import os
import sys

path = '/home/yourusername/yourproject'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 5. Environment variables

Set the following in the PythonAnywhere web app "Environment variables" section:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=yourusername.pythonanywhere.com`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_HOST_USER`
- `EMAIL_HOST` (usually `smtp.gmail.com`)
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `DATABASE_URL` (optional if you use a remote database)
- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`

## 6. Static files

- On PythonAnywhere, set the static files mapping to serve `STATIC_ROOT`.
- Run:

```bash
python manage.py collectstatic --noinput
```

## 7. Database

If using `db.sqlite3` on PythonAnywhere, ensure the file is in the project root and writable by the web app.

For a production DB, use an external database and set `DATABASE_URL` accordingly.

## 8. Testing

- Reload the web app after changes.
- Check the error logs if anything fails.
- Use the built-in console to run:

```bash
python manage.py migrate
python manage.py createsuperuser
```

## 9. Notes

- Remove any Render-specific files from the repo.
- PythonAnywhere uses its own web app configuration; no `render.yaml`, `gunicorn.conf.py`, or Render build scripts are required.

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
3. Choose the Python version matching this project (Python 3.10 is the recommended runtime on your account).
4. Set the source code folder to the repository clone location.
5. Set the virtualenv path to `/home/taqdeesgolandaz/.virtualenvs/fitzone`.

## 4. Configure the web app

- In the "WSGI configuration file" section, update the WSGI file to use your project path and virtual environment.
- Example `WSGI configuration` snippet:

```python
import sys
import os

path = '/home/taqdeesgolandaz/fitzone-django-project'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')

activate_this = '/home/taqdeesgolandaz/.virtualenvs/fitzone/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 5. Environment variables

Set the following in the PythonAnywhere web app "Environment variables" section:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=fitzone-django-project.pythonanywhere.com`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_HOST_USER`
- `EMAIL_HOST` (usually `smtp.gmail.com`)
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `EMAIL_USE_SSL=False`
- `DEFAULT_FROM_EMAIL=FitZone <your-email@gmail.com>`
- `SITE_URL=https://fitzone-django-project.pythonanywhere.com`
- `DATABASE_URL` (optional if you use a remote database)
- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`

If your PythonAnywhere app name is different, replace `fitzone-django-project` with your actual app name.

## 6. Static files

- On PythonAnywhere, set the static files mapping as follows:

  - URL: `/static/`
    Directory: `/home/taqdeesgolandaz/fitzone-django-project/staticfiles/`
  - URL: `/media/`
    Directory: `/home/taqdeesgolandaz/fitzone-django-project/media/`

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

## 9. App URL

Your application should be available at:

```text
https://fitzone-django-project.pythonanywhere.com
```

If your app uses a different PythonAnywhere subdomain, replace `fitzone-django-project` with the actual application name.

## 10. Notes

- Remove any Render-specific files from the repo.
- PythonAnywhere uses its own web app configuration; no `render.yaml`, `gunicorn.conf.py`, or Render build scripts are required.

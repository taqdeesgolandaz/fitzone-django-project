# FitZone PythonAnywhere Deployment Guide

**Last Updated:** June 25, 2026  
**Status:** Ready for Deployment

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Step 1: Prepare Your Local Environment](#step-1-prepare-your-local-environment)
3. [Step 2: Push Code to GitHub](#step-2-push-code-to-github)
4. [Step 3: Set Up PythonAnywhere Account](#step-3-set-up-pythonanywhere-account)
5. [Step 4: Clone Project on PythonAnywhere](#step-4-clone-project-on-pythonanywhere)
6. [Step 5: Configure Virtual Environment](#step-5-configure-virtual-environment)
7. [Step 6: Configure Django Settings](#step-6-configure-django-settings)
8. [Step 7: Set Up Static Files](#step-7-set-up-static-files)
9. [Step 8: Create WSGI Configuration](#step-8-create-wsgi-configuration)
10. [Step 9: Configure Environment Variables](#step-9-configure-environment-variables)
11. [Step 10: Initialize Database](#step-10-initialize-database)
12. [Step 11: Reload Web App](#step-11-reload-web-app)
13. [Testing & Troubleshooting](#testing--troubleshooting)
14. [Production Security Checklist](#production-security-checklist)

---

## Pre-Deployment Checklist

Before starting, ensure you have:

- [ ] GitHub account with repository access
- [ ] PythonAnywhere account (Free or Paid)
- [ ] Production SECRET_KEY generated
- [ ] Razorpay API keys (live or test)
- [ ] Gmail/Email SMTP credentials
- [ ] List of allowed domains/hosts
- [ ] .env file created locally with all values
- [ ] All requirements.txt dependencies tested locally
- [ ] Git initialized and code committed

---

## Step 1: Prepare Your Local Environment

### 1.1 Update Your Local .env File

Create a `.env` file in your project root (this will NOT be committed to GitHub):

```bash
# Production Settings
DEBUG=False
SECRET_KEY=your-production-secret-key-here-generate-it
ALLOWED_HOSTS=your-username.pythonanywhere.com

# Database (leave empty for SQLite, set for PostgreSQL)
DATABASE_URL=

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=FitZone <your-gmail@gmail.com>
SERVER_EMAIL=your-gmail@gmail.com

# Razorpay (Use test keys for testing, live keys for production)
RAZORPAY_KEY_ID=rzp_live_YourLiveKeyID
RAZORPAY_KEY_SECRET=YourLiveKeySecret

# Security
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0

# Site URL
SITE_URL=https://your-username.pythonanywhere.com
```

### 1.2 Generate a Production SECRET_KEY

Run this in your local terminal:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it into your `.env` file as `SECRET_KEY`.

### 1.3 Test Locally

Ensure everything works locally:

```bash
source myenv/Scripts/activate  # On Windows: myenv\Scripts\activate
python manage.py runserver
```

Visit `http://127.0.0.1:8000` and verify the site works.

---

## Step 2: Push Code to GitHub

### 2.1 Initialize Git (if not already done)

```bash
cd "c:\Users\GLOBAL T\Desktop\FitZone"
git init
git add .
git commit -m "Initial commit - FitZone Django project ready for deployment"
```

### 2.2 Create Remote Repository

1. Go to [GitHub.com](https://github.com/new)
2. Create a new repository named `fitzone` (or your preferred name)
3. Do NOT initialize with README, .gitignore, or license

### 2.3 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/fitzone.git
git branch -M main
git push -u origin main
```

**Important:** Make sure `.env` is in `.gitignore` so secrets are NOT pushed!

---

## Step 3: Set Up PythonAnywhere Account

### 3.1 Create Account

1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Click "Sign up for Beginner account" (Free tier available)
3. Choose username (this will be part of your domain: `username.pythonanywhere.com`)
4. Verify email

### 3.2 Account Settings

1. Go to your Account page
2. Note your username (e.g., `taqdeesgolandaz`)
3. Go to "Web" tab and click "Add a new web app"

---

## Step 4: Clone Project on PythonAnywhere

### 4.1 Open Bash Console

On PythonAnywhere:
1. Go to "Consoles" tab
2. Click "Start a new console" → "Bash"

### 4.2 Clone Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/fitzone.git fitzone-django-project
cd fitzone-django-project
ls -la
```

Verify you see `manage.py`, `requirements.txt`, `fitzone/`, etc.

---

## Step 5: Configure Virtual Environment

### 5.1 Create Virtual Environment

In the PythonAnywhere Bash console:

```bash
mkvirtualenv --python=/usr/bin/python3.10 fitzone
# Or use python3.11 if available
```

### 5.2 Install Dependencies

```bash
pip install -r requirements.txt
```

Wait for installation to complete. This may take 2-5 minutes.

### 5.3 Verify Installation

```bash
pip list | grep -E "Django|gunicorn|whitenoise"
```

You should see Django 5.0.10, gunicorn, and whitenoise in the list.

---

## Step 6: Configure Django Settings

Your `fitzone/settings.py` is already configured to use environment variables. It will:
- Use SQLite3 by default (no DATABASE_URL needed)
- Load email settings from env vars
- Load Razorpay keys from env vars
- Handle ALLOWED_HOSTS from env vars

No changes needed here! The settings will automatically load from PythonAnywhere's environment variables.

---

## Step 7: Set Up Static Files

### 7.1 Collect Static Files

In PythonAnywhere Bash console:

```bash
cd ~/fitzone-django-project
workon fitzone
python manage.py collectstatic --noinput
```

This creates `/staticfiles/` directory with all CSS, JS, and images.

### 7.2 Verify

```bash
ls -la staticfiles/
```

You should see `admin/`, `rest_framework/`, `css/`, `js/`, etc.

---

## Step 8: Create WSGI Configuration

### 8.1 Edit WSGI File

On PythonAnywhere:
1. Go to "Web" tab
2. Click on your web app (e.g., `taqdeesgolandaz.pythonanywhere.com`)
3. Scroll to "Code" section
4. Click the WSGI configuration file link (usually shows a path like `/var/www/...`)

### 8.2 Update WSGI Configuration

Replace the entire content with:

```python
import sys
import os
from pathlib import Path

# Add project directory to Python path
home_dir = os.path.expanduser("~")
project_dir = os.path.join(home_dir, 'fitzone-django-project')

if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Change working directory
os.chdir(project_dir)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'fitzone.settings'

# Import and get WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Save the file.**

---

## Step 9: Configure Environment Variables

### 9.1 Add Environment Variables on PythonAnywhere

1. Go to "Web" tab
2. Click on your web app
3. Scroll down to "Environment variables"
4. Click "Add a new variable"

Add the following variables (click "Add" after each):

| Variable Name | Value |
|---|---|
| `DEBUG` | `False` |
| `SECRET_KEY` | `your-generated-secret-key-from-step-1` |
| `ALLOWED_HOSTS` | `taqdeesgolandaz.pythonanywhere.com` |
| `EMAIL_HOST_USER` | `your-gmail@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `your-app-specific-password` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `DEFAULT_FROM_EMAIL` | `FitZone <your-gmail@gmail.com>` |
| `SERVER_EMAIL` | `your-gmail@gmail.com` |
| `RAZORPAY_KEY_ID` | `rzp_test_SwU8wO2DuOpWoo` |
| `RAZORPAY_KEY_SECRET` | `hS7jKWDqXYQRbo3IoS6J3oMB` |
| `SITE_URL` | `https://taqdeesgolandaz.pythonanywhere.com` |

**Important:** Replace `taqdeesgolandaz` with your actual PythonAnywhere username.

---

## Step 10: Initialize Database

### 10.1 Run Migrations

In PythonAnywhere Bash console:

```bash
cd ~/fitzone-django-project
workon fitzone
python manage.py migrate
```

Wait for migrations to complete. You should see output like:
```
Running migrations:
  Applying admin.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### 10.2 Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: `admin` (or your preferred username)
- Email: `your-email@gmail.com`
- Password: Create a strong password

**Save these credentials securely!**

### 10.3 Create Initial Admin User

```bash
python manage.py shell
```

Then run:
```python
from accounts.models import CustomUser
from django.contrib.auth.models import Group

# Create superuser if not already created
admin_user = CustomUser.objects.create_superuser(
    username='admin',
    email='admin@fitzone.com',
    password='secure_password_here',
    is_staff=True,
    is_superuser=True
)
print(f"Admin user created: {admin_user}")
exit()
```

---

## Step 11: Set Up Static Files Mapping

### 11.1 Configure Static Files on PythonAnywhere

1. Go to "Web" tab
2. Click your web app
3. Scroll to "Static files and directories"
4. Add the following mappings:

| URL | Directory |
|---|---|
| `/static/` | `/home/taqdeesgolandaz/fitzone-django-project/staticfiles/` |
| `/media/` | `/home/taqdeesgolandaz/fitzone-django-project/media/` |

Replace `taqdeesgolandaz` with your username.

**Click "Save"**

---

## Step 12: Reload Web App

### 12.1 Reload the Web App

1. On PythonAnywhere "Web" tab
2. Click your web app
3. Scroll to top
4. Click the green "Reload" button

Wait 10-15 seconds for the app to restart.

---

## Testing & Troubleshooting

### Test 1: Check Your Site

1. Visit `https://your-username.pythonanywhere.com` in your browser
2. You should see the FitZone homepage

### Test 2: Admin Panel

1. Visit `https://your-username.pythonanywhere.com/admin/`
2. Log in with your superuser credentials
3. You should see the Django admin interface

### Test 3: API Endpoints

1. Visit `https://your-username.pythonanywhere.com/api/` (if configured)
2. Test endpoints like user login, membership info, etc.

### Test 4: Email

Send a test email:
1. Log in to admin panel
2. Go to Accounts → CustomUsers
3. Select a user and send a test email (or modify your app to send one)

### Common Issues

#### Issue: 500 Internal Server Error

**Solution:** Check error logs
```bash
cd ~/fitzone-django-project
tail -50 /var/log/taqdeesgolandaz.pythonanywhere.com.error.log
```

#### Issue: Static Files Not Loading (404 errors on CSS/JS)

**Solution:** Recollect static files
```bash
python manage.py collectstatic --noinput
```

Then reload web app on PythonAnywhere.

#### Issue: "DisallowedHost" Error

**Solution:** Update ALLOWED_HOSTS in environment variables to include your domain.

#### Issue: Email Not Sending

**Solution:**
1. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct
2. Enable "Less secure app access" in Gmail (or use App Passwords)
3. Check error logs for SMTP errors

#### Issue: Database Locked

**Solution:**
```bash
python manage.py migrate --no-input
```

If still locked, try:
```bash
rm db.sqlite3
python manage.py migrate
```

---

## Production Security Checklist

Before going live, verify:

- [ ] `DEBUG = False` in environment variables
- [ ] `SECRET_KEY` is strong and unique
- [ ] `ALLOWED_HOSTS` includes your PythonAnywhere domain
- [ ] All email credentials are correct
- [ ] Razorpay keys are production keys (not test keys)
- [ ] Database has at least one superuser
- [ ] SSL is enabled (https://) - PythonAnywhere provides free SSL
- [ ] Static files are served correctly
- [ ] Media files directory exists and is writable
- [ ] Error logs are being monitored
- [ ] Backups of db.sqlite3 are being taken

---

## Next Steps After Deployment

1. **Set up automated backups:**
   ```bash
   # Create a backup script
   ```

2. **Monitor error logs:**
   - Check `/var/log/taqdeesgolandaz.pythonanywhere.com.error.log` regularly

3. **Test all features:**
   - User registration
   - Membership payments
   - Workout tracking
   - Email notifications
   - Admin dashboard

4. **Configure domain (Optional):**
   - PythonAnywhere supports custom domains
   - Update ALLOWED_HOSTS when using custom domain

5. **Scale if needed:**
   - Upgrade to Paid account if free tier has limitations
   - Consider Redis for caching

---

## Support & Documentation

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Django Deployment](https://docs.djangoproject.com/en/5.0/howto/deployment/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)

---

**Deployment completed! Your FitZone app is now live on PythonAnywhere! 🎉**

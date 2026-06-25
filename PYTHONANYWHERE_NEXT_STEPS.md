# 🚀 PythonAnywhere Next Steps (Continue Deployment)

**Your code is now on GitHub with migrations!**

Run these commands in PythonAnywhere Bash Console in order:

---

## Step 1: Pull Latest Code

```bash
cd ~/fitzone-django-project
git pull origin main
```

Expected output: Should see the new migrations and deployment files.

---

## Step 2: Run Migrations

```bash
workon fitzone
python manage.py makemigrations --dry-run  # Check what would be applied
python manage.py migrate
```

Expected: All migrations applied successfully.

---

## Step 3: Collect Static Files Again

```bash
python manage.py collectstatic --noinput
```

Expected: "165 static files copied"

---

## Step 4: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow prompts:
- Username: `admin` (or your preference)
- Email: `your-email@gmail.com`
- Password: (create a strong one)

---

## Step 5: Update WSGI Configuration

On PythonAnywhere Web page:
1. Go to **Web** tab
2. Click your web app (taqdeesgolandaz.pythonanywhere.com)
3. Scroll to **"Code"** section
4. Click the **WSGI configuration file** link
5. Replace content with this:

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

**Click "Save"**

---

## Step 6: Set Environment Variables

In PythonAnywhere Web page (same page, scroll down):

Click **"Environment variables"** and add these:

| Variable | Value |
|---|---|
| `DEBUG` | `False` |
| `SECRET_KEY` | `(use your generated key)` |
| `ALLOWED_HOSTS` | `taqdeesgolandaz.pythonanywhere.com` |
| `EMAIL_HOST_USER` | `your-gmail@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `your-gmail-app-password` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `DEFAULT_FROM_EMAIL` | `FitZone <your-gmail@gmail.com>` |
| `SERVER_EMAIL` | `your-gmail@gmail.com` |
| `RAZORPAY_KEY_ID` | `rzp_test_SwU8wO2DuOpWoo` |
| `RAZORPAY_KEY_SECRET` | `hS7jKWDqXYQRbo3IoS6J3oMB` |
| `SITE_URL` | `https://taqdeesgolandaz.pythonanywhere.com` |

For each variable: Click "Add" → Enter name → Enter value → Click checkbox → Repeat

---

## Step 7: Configure Static Files Mapping

Same web app page, scroll to **"Static files and directories"**:

Add these mappings:

| URL | Directory |
|---|---|
| `/static/` | `/home/taqdeesgolandaz/fitzone-django-project/staticfiles/` |
| `/media/` | `/home/taqdeesgolandaz/fitzone-django-project/media/` |

Click **"Save"** after adding both.

---

## Step 8: Reload Web App

**At the top of the page, click the green "Reload" button**

Wait 10-15 seconds for app to restart.

---

## Step 9: Test Your Site

Visit these URLs in your browser:

1. **Homepage:** `https://taqdeesgolandaz.pythonanywhere.com`
   - Should show FitZone homepage
   - CSS/JS should load (page looks styled)

2. **Admin Panel:** `https://taqdeesgolandaz.pythonanywhere.com/admin/`
   - Log in with superuser credentials
   - Should see Django admin interface

3. **Check for errors:** Open browser console (F12)
   - Should have NO 404 errors
   - Should have NO 500 errors

---

## Troubleshooting

### If you get "DisallowedHost" error:
→ Check ALLOWED_HOSTS environment variable is correct

### If CSS/JS not loading (page looks unstyled):
→ Run: `python manage.py collectstatic --noinput`
→ Then reload web app

### If you get 500 error:
→ Check error logs: `tail -50 /var/log/taqdeesgolandaz.pythonanywhere.com.error.log`

### If database error:
→ Run: `python manage.py migrate`

---

## Success Checklist

- [ ] Code pulled from GitHub
- [ ] Migrations applied successfully
- [ ] Static files collected
- [ ] Superuser created
- [ ] WSGI file updated
- [ ] All environment variables set
- [ ] Static files mapping configured
- [ ] Web app reloaded
- [ ] Homepage loads without errors
- [ ] Admin panel accessible
- [ ] No 404 or 500 errors

---

**After all steps above are complete, your FitZone app will be LIVE! 🎉**

Follow these steps in order in your PythonAnywhere Bash console and web settings.

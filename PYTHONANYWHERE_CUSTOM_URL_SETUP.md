# Change PythonAnywhere URL to fitzone-application

## Option 1: Create New Web App with Custom Name (Recommended)

### Step 1: Create New Web App on PythonAnywhere

1. Go to PythonAnywhere Dashboard
2. Click **"Web"** tab
3. Click **"Add a new web app"**
4. Choose **"Manual configuration"** (NOT "Django")
5. Select **Python 3.10**
6. **IMPORTANT:** Name it: `fitzone-application` (this becomes your domain!)
   - Your new URL will be: `https://fitzone-application.pythonanywhere.com`

### Step 2: Configure the New App

After creating, you'll see a new web app at the bottom. Click on it.

#### 2.1 Update Source Code Path

- Scroll to **"Code"** section
- Set **"Source code"** to: `/home/taqdeesgolandaz/fitzone-django-project`
- Set **"Working directory"** to: `/home/taqdeesgolandaz/fitzone-django-project`

#### 2.2 Set Virtual Environment Path

- Set to: `/home/taqdeesgolandaz/.virtualenvs/fitzone`

#### 2.3 Update WSGI Configuration File

Click the WSGI configuration file link and replace with:

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

### Step 3: Set Environment Variables for New App

Scroll down to **"Environment variables"** on the same page and add:

| Variable | Value |
|---|---|
| `DEBUG` | `False` |
| `SECRET_KEY` | `(your-generated-key)` |
| `ALLOWED_HOSTS` | `fitzone-application.pythonanywhere.com` |
| `EMAIL_HOST_USER` | `your-gmail@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `your-gmail-app-password` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `DEFAULT_FROM_EMAIL` | `FitZone <your-gmail@gmail.com>` |
| `SERVER_EMAIL` | `your-gmail@gmail.com` |
| `RAZORPAY_KEY_ID` | `rzp_test_SwU8wO2DuOpWoo` |
| `RAZORPAY_KEY_SECRET` | `hS7jKWDqXYQRbo3IoS6J3oMB` |
| `SITE_URL` | `https://fitzone-application.pythonanywhere.com` |

**Important:** Update `ALLOWED_HOSTS` and `SITE_URL` to use `fitzone-application.pythonanywhere.com`

### Step 4: Configure Static Files Mapping

Same page, scroll to **"Static files and directories"**:

Add these mappings:

| URL | Directory |
|---|---|
| `/static/` | `/home/taqdeesgolandaz/fitzone-django-project/staticfiles/` |
| `/media/` | `/home/taqdeesgolandaz/fitzone-django-project/media/` |

Click **"Save"**

### Step 5: Reload the New Web App

- Click the green **"Reload"** button at the top
- Wait 10-15 seconds

### Step 6: Delete Old Web App (Optional)

Once new app is working, you can delete the old `taqdeesgolandaz.pythonanywhere.com` app:

1. Go to **"Web"** tab
2. Click on the old app name
3. Scroll down to **"Delete this web app"**
4. Confirm deletion

---

## Option 2: Use Custom Domain (Paid Account)

If you have a paid PythonAnywhere account:

1. Go to **"Web"** tab
2. Click on your web app
3. Scroll to **"Domain name"** section
4. Add custom domain: `fitzone-application.com` (if you own it)
5. Update DNS records with PythonAnywhere's nameservers

---

## Testing Your New URL

After reload, visit:

- **Homepage:** `https://fitzone-application.pythonanywhere.com`
- **Admin:** `https://fitzone-application.pythonanywhere.com/admin/`

Login with:
- Username: `admin`
- Password: `admin123`

---

## Update Environment Variables Checklist

After creating new app, make sure you updated:

- [ ] `ALLOWED_HOSTS` = `fitzone-application.pythonanywhere.com`
- [ ] `SITE_URL` = `https://fitzone-application.pythonanywhere.com`
- [ ] All other env vars (EMAIL, RAZORPAY, etc.)
- [ ] WSGI file configured correctly
- [ ] Static files mapped
- [ ] Web app reloaded

---

## Troubleshooting

### If you get "DisallowedHost" error:
→ Check `ALLOWED_HOSTS` environment variable

### If CSS/JS not loading:
→ Run in PythonAnywhere console:
```bash
cd ~/fitzone-django-project
workon fitzone
python manage.py collectstatic --noinput
```

### If you see old app's data:
→ Both apps use same database, so data is shared (this is good!)

---

## Summary

**New Production URL:** `https://fitzone-application.pythonanywhere.com`

This is much better than the default username-based URL! 🎉

Follow Option 1 above to set it up.

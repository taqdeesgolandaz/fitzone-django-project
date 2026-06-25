# PythonAnywhere Deployment Checklist

Use this checklist to ensure all deployment steps are completed successfully.

---

## Phase 1: Pre-Deployment (Local)

- [ ] **1.1** Generated production SECRET_KEY and saved it
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] **1.2** Created `.env` file with all production values
  - [ ] SECRET_KEY ✓
  - [ ] DEBUG=False ✓
  - [ ] ALLOWED_HOSTS set ✓
  - [ ] EMAIL credentials added ✓
  - [ ] Razorpay keys added ✓

- [ ] **1.3** Verified `.env` is in `.gitignore`
  ```bash
  cat .gitignore | grep ".env"
  ```

- [ ] **1.4** Tested project locally
  ```bash
  python manage.py runserver
  ```

- [ ] **1.5** Git initialized and code committed
  ```bash
  git log --oneline | head -5
  ```

---

## Phase 2: GitHub Setup

- [ ] **2.1** Created GitHub repository
  - Repository name: `fitzone` (or custom name)
  - Visibility: Public/Private (your choice)

- [ ] **2.2** Added remote origin
  ```bash
  git remote -v
  # Should show: origin https://github.com/YOUR_USERNAME/fitzone.git
  ```

- [ ] **2.3** Pushed code to main branch
  ```bash
  git branch
  # Should show: * main
  ```

- [ ] **2.4** Verified on GitHub
  - [ ] Code is visible on GitHub
  - [ ] `.env` file is NOT in repository
  - [ ] All source files are present

---

## Phase 3: PythonAnywhere Account

- [ ] **3.1** Created PythonAnywhere account
  - Username: ________________
  - Email verified: Yes/No

- [ ] **3.2** Note your username
  - Your domain will be: `{username}.pythonanywhere.com`
  - Username: ________________

---

## Phase 4: Project Setup on PythonAnywhere

- [ ] **4.1** Opened Bash console on PythonAnywhere

- [ ] **4.2** Cloned repository
  ```bash
  cd ~
  git clone https://github.com/YOUR_USERNAME/fitzone.git fitzone-django-project
  cd fitzone-django-project
  ls -la
  ```
  - [ ] `manage.py` exists
  - [ ] `requirements.txt` exists
  - [ ] `fitzone/` directory exists

- [ ] **4.3** Created virtual environment
  ```bash
  mkvirtualenv --python=/usr/bin/python3.10 fitzone
  ```
  - [ ] Virtual environment created
  - [ ] Activated automatically

- [ ] **4.4** Installed dependencies
  ```bash
  pip install -r requirements.txt
  ```
  - [ ] Installation completed without errors
  - [ ] Django 5.0.10 installed
  - [ ] gunicorn installed
  - [ ] whitenoise installed
  - Installation time: _______ minutes

- [ ] **4.5** Verified installation
  ```bash
  pip list | grep Django
  pip list | grep gunicorn
  pip list | grep whitenoise
  ```

---

## Phase 5: Django Configuration

- [ ] **5.1** Settings already configured for production
  - `fitzone/settings.py` uses environment variables ✓
  - WhiteNoise middleware configured ✓
  - Database settings flexible (SQLite/PostgreSQL) ✓

- [ ] **5.2** Checked settings for customizations needed
  - No changes required to settings.py for standard deployment ✓

---

## Phase 6: Static Files

- [ ] **6.1** Collected static files
  ```bash
  cd ~/fitzone-django-project
  workon fitzone
  python manage.py collectstatic --noinput
  ```
  - [ ] `staticfiles/` directory created
  - [ ] No errors during collection

- [ ] **6.2** Verified static files
  ```bash
  ls -la staticfiles/ | head -20
  du -sh staticfiles/
  ```
  - [ ] Multiple directories present (admin, rest_framework, etc.)
  - [ ] Total size: _______ MB

---

## Phase 7: WSGI Configuration

- [ ] **7.1** Accessed WSGI configuration file
  - Path on PythonAnywhere: `/var/www/...pythonanywhere_com_wsgi.py`

- [ ] **7.2** Updated WSGI file content
  - [ ] Added project to sys.path
  - [ ] Set DJANGO_SETTINGS_MODULE
  - [ ] Changed working directory
  - [ ] Imported get_wsgi_application()

- [ ] **7.3** Saved WSGI file
  - [ ] File saved successfully
  - [ ] No syntax errors

---

## Phase 8: Environment Variables

On PythonAnywhere Web App settings, added:

- [ ] **DEBUG** = `False`
- [ ] **SECRET_KEY** = `{your-generated-key}`
- [ ] **ALLOWED_HOSTS** = `{username}.pythonanywhere.com`
- [ ] **EMAIL_HOST_USER** = `{your-email@gmail.com}`
- [ ] **EMAIL_HOST_PASSWORD** = `{your-app-specific-password}`
- [ ] **EMAIL_HOST** = `smtp.gmail.com`
- [ ] **EMAIL_PORT** = `587`
- [ ] **EMAIL_USE_TLS** = `True`
- [ ] **DEFAULT_FROM_EMAIL** = `FitZone <{your-email@gmail.com}>`
- [ ] **SERVER_EMAIL** = `{your-email@gmail.com}`
- [ ] **RAZORPAY_KEY_ID** = `{your-key-id}`
- [ ] **RAZORPAY_KEY_SECRET** = `{your-key-secret}`
- [ ] **SITE_URL** = `https://{username}.pythonanywhere.com`

Verification:
```bash
python -c "import os; print('SECRET_KEY:', len(os.environ.get('SECRET_KEY', '')))"
python -c "import os; print('DEBUG:', os.environ.get('DEBUG', ''))"
```

---

## Phase 9: Database & Migrations

- [ ] **9.1** Ran migrations
  ```bash
  cd ~/fitzone-django-project
  workon fitzone
  python manage.py migrate
  ```
  - [ ] All migrations applied successfully
  - [ ] No errors in output

- [ ] **9.2** Created superuser
  ```bash
  python manage.py createsuperuser
  ```
  - Username: `________________`
  - Email: `________________`
  - Password: `(secure password saved)`

- [ ] **9.3** Verified database
  ```bash
  ls -la db.sqlite3
  ```
  - [ ] Database file exists
  - [ ] File size > 0

---

## Phase 10: Static Files Mapping

In PythonAnywhere Web App settings:

- [ ] **10.1** Added URL mapping for static files
  - URL: `/static/`
  - Directory: `/home/{username}/fitzone-django-project/staticfiles/`

- [ ] **10.2** Added URL mapping for media files
  - URL: `/media/`
  - Directory: `/home/{username}/fitzone-django-project/media/`

- [ ] **10.3** Clicked "Save"

---

## Phase 11: Deploy & Reload

- [ ] **11.1** Clicked "Reload" button on PythonAnywhere
  - [ ] Green reload button clicked
  - [ ] Waited 10-15 seconds for app to restart

- [ ] **11.2** Checked that app is running
  - [ ] Web tab shows "Pythonanywhere" or green checkmark
  - [ ] No "Failed" status

---

## Phase 12: Testing

### Basic Site Access

- [ ] **12.1** Site homepage loads
  ```
  Visit: https://{username}.pythonanywhere.com
  Expected: FitZone homepage visible
  Actual: ________________________
  ```

- [ ] **12.2** Admin panel accessible
  ```
  Visit: https://{username}.pythonanywhere.com/admin/
  Login: superuser credentials
  Expected: Django admin interface
  Actual: ________________________
  ```

### Feature Testing

- [ ] **12.3** API endpoints work (if configured)
  ```
  Visit: https://{username}.pythonanywhere.com/api/
  Expected: API root page loads
  Actual: ________________________
  ```

- [ ] **12.4** CSS/JS files load correctly
  - [ ] Page styling looks normal (not unstyled)
  - [ ] JavaScript interactions work
  - Check browser console (F12) for 404 errors: ✓/✗

- [ ] **12.5** Media files serve correctly
  - [ ] User profile pictures load (if any)
  - [ ] Trainer images load (if any)

### Error Monitoring

- [ ] **12.6** No errors in logs
  ```bash
  tail -100 /var/log/{username}.pythonanywhere.com.error.log
  ```
  - [ ] No 500 errors
  - [ ] No 404 errors on essential assets

- [ ] **12.7** Email sending configured
  - [ ] Test email endpoint works
  - [ ] Emails reach inbox (not spam)

---

## Phase 13: Production Security

- [ ] **13.1** DEBUG is False
  ```bash
  python -c "import os; print('DEBUG:', os.environ.get('DEBUG'))"
  ```

- [ ] **13.2** SECRET_KEY is strong and unique
  - [ ] Contains mix of upper, lower, numbers, symbols
  - [ ] Not the Django default
  - [ ] At least 50 characters

- [ ] **13.3** ALLOWED_HOSTS is correctly set
  ```bash
  python manage.py check
  ```
  - [ ] No DisallowedHost warnings

- [ ] **13.4** HTTPS is enabled
  - [ ] URL shows `https://` (not `http://`)
  - [ ] Padlock icon visible in browser

- [ ] **13.5** Database backups planned
  - [ ] Local backup created: `db.sqlite3.backup`
  - [ ] Backup schedule documented

---

## Phase 14: Final Verification

- [ ] **14.1** All environment variables set
  ```bash
  python manage.py shell -c "
  import os
  vars = ['DEBUG', 'SECRET_KEY', 'ALLOWED_HOSTS', 'EMAIL_HOST_USER', 'RAZORPAY_KEY_ID']
  for var in vars:
      val = os.environ.get(var, 'NOT SET')
      print(f'{var}: {val[:20]}...' if len(str(val)) > 20 else f'{var}: {val}')
  "
  ```

- [ ] **14.2** Settings test passes
  ```bash
  python manage.py check
  ```
  - [ ] Output: "System check identified no issues (0 silenced)."

- [ ] **14.3** Final site test
  - [ ] Homepage loads: ✓
  - [ ] Admin panel works: ✓
  - [ ] User can register: ✓
  - [ ] Payment gateway loads: ✓

- [ ] **14.4** Error log is clean
  - [ ] No critical errors
  - [ ] Warnings are acceptable

---

## 🎉 Deployment Complete!

**Deployment Date:** ________________  
**Deployed By:** ________________  
**Production URL:** `https://{username}.pythonanywhere.com`  
**Admin URL:** `https://{username}.pythonanywhere.com/admin/`  

### Next Steps

1. Share production URL with team
2. Perform full user acceptance testing (UAT)
3. Monitor error logs daily for first week
4. Set up automated backups
5. Document any issues and resolutions
6. Plan database maintenance schedule

### Important Credentials

| Item | Value | Location |
|---|---|---|
| Admin Username | `________________` | Secure storage |
| Superuser Email | `________________` | Secure storage |
| Admin Password | `(securely saved)` | Secure storage |
| Production URL | `https://{username}.pythonanywhere.com` | Shared with team |

---

**✅ All checks passed! Your FitZone application is live!**

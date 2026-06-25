# 🚀 FitZone Koyeb Deployment - Quick Checklist

## Phase 1: Pre-Deployment (Local Machine)

- [ ] **1.1** Generated production SECRET_KEY
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] **1.2** Tested project locally
  ```bash
  myenv\Scripts\activate
  python manage.py runserver
  # Visited http://127.0.0.1:8000 ✓
  ```

- [ ] **1.3** Created Gmail app password
  - Go to: https://myaccount.google.com/apppasswords
  - Generated 16-character password
  - Saved it: `________________`

- [ ] **1.4** Gathered Razorpay keys
  - Test Key ID: `rzp_test_SwU8wO2DuOpWoo`
  - Test Key Secret: `hS7jKWDqXYQRbo3IoS6J3oMB`
  - (Or live keys if ready)

- [ ] **1.5** Verified deployment files exist
  ```bash
  ls -la Dockerfile Procfile docker-compose.yml .dockerignore
  ```
  - All 4 files present ✓

---

## Phase 2: GitHub Preparation

- [ ] **2.1** Committed deployment files
  ```bash
  git add Dockerfile Procfile docker-compose.yml .dockerignore
  git commit -m "Add Koyeb deployment configuration"
  ```

- [ ] **2.2** Pushed to GitHub
  ```bash
  git push origin main
  ```

- [ ] **2.3** Verified on GitHub
  - Visit: https://github.com/YOUR_USERNAME/fitzone-django-project
  - See Dockerfile, Procfile, etc. ✓

---

## Phase 3: Koyeb Account Setup

- [ ] **3.1** Created Koyeb account
  - Go to: https://www.koyeb.com/sign-up
  - Recommended: Sign up with GitHub
  - Email verified ✓

- [ ] **3.2** Authorized GitHub access
  - Koyeb can access your repositories ✓

---

## Phase 4: Service Deployment

- [ ] **4.1** Created new service in Koyeb
  - Click: "Create Service" or "Deploy"
  - Selected: GitHub as source

- [ ] **4.2** Connected GitHub repository
  - Repository: `fitzone-django-project`
  - Branch: `main` ✓

- [ ] **4.3** Configured deployment settings
  - Builder: `Dockerfile` ✓
  - Port: `8000` ✓
  - Name: `fitzone-app` (or your name)

---

## Phase 5: Environment Variables

Set these in Koyeb Dashboard:

### Core Django Settings

- [ ] `DEBUG` = `False`
- [ ] `SECRET_KEY` = `(your-generated-key)`
- [ ] `ALLOWED_HOSTS` = `*.koyeb.app,localhost,127.0.0.1`
- [ ] `DATABASE_URL` = (leave empty for SQLite)

### Email Configuration (Gmail)

- [ ] `EMAIL_HOST_USER` = `your-email@gmail.com`
- [ ] `EMAIL_HOST_PASSWORD` = `(your-app-password)`
- [ ] `EMAIL_HOST` = `smtp.gmail.com`
- [ ] `EMAIL_PORT` = `587`
- [ ] `EMAIL_USE_TLS` = `True`
- [ ] `DEFAULT_FROM_EMAIL` = `FitZone <your-email@gmail.com>`
- [ ] `SERVER_EMAIL` = `your-email@gmail.com`

### Razorpay Keys

- [ ] `RAZORPAY_KEY_ID` = `rzp_test_SwU8wO2DuOpWoo` (or live)
- [ ] `RAZORPAY_KEY_SECRET` = `hS7jKWDqXYQRbo3IoS6J3oMB` (or live)

### Site Configuration

- [ ] `SITE_URL` = `https://fitzone-yourname-xxxx.koyeb.app`

### Python Settings

- [ ] `PYTHONUNBUFFERED` = `1`
- [ ] `PYTHONDONTWRITEBYTECODE` = `1`

---

## Phase 6: Deploy & Monitor

- [ ] **6.1** Clicked "Deploy" button
  - Service creation started ✓

- [ ] **6.2** Monitored deployment
  - Watched "Activity" tab
  - Build started → Building → Built → Deploying → Running
  - Expected time: 2-5 minutes

- [ ] **6.3** Checked status
  - Service status: **Running** (green) ✓
  - Replicas: **1/1** ✓
  - Build logs: No errors ✓

- [ ] **6.4** Copied public URL
  - URL format: `https://fitzone-yourname-xxxx.koyeb.app`
  - Saved: `____________________________`

---

## Phase 7: Testing

### Basic Functionality

- [ ] **7.1** Homepage loads
  ```
  Visit: https://fitzone-yourname-xxxx.koyeb.app
  Expected: FitZone homepage visible ✓
  Styling: CSS/JS loaded (page looks styled) ✓
  ```

- [ ] **7.2** Admin panel accessible
  ```
  Visit: https://fitzone-yourname-xxxx.koyeb.app/admin/
  Login: admin / admin123
  Expected: Django admin interface ✓
  ```

- [ ] **7.3** User registration works
  ```
  Go to: /register/
  Create test account
  Verify email sends (check spam) ✓
  ```

- [ ] **7.4** Check browser console
  ```
  Press: F12
  Expected: No 404 errors on CSS/JS
  Expected: No 500 errors ✓
  ```

### Database & Migrations

- [ ] **7.5** Database created
  ```
  Koyeb Logs show:
  "Running migrations..."
  "Applying..."
  "OK" ✓
  ```

- [ ] **7.6** Superuser exists
  - Admin login works: admin / admin123 ✓

---

## Phase 8: Monitoring

- [ ] **8.1** Viewed service logs
  - Koyeb Dashboard → Service → Logs
  - Saw successful startup messages ✓

- [ ] **8.2** Checked error logs
  - No critical errors ✓
  - Some warnings are normal

- [ ] **8.3** Verified auto-deployment
  - Made local code change
  - Committed: `git push origin main`
  - Koyeb automatically redeployed ✓

---

## Phase 9: Post-Deployment

- [ ] **9.1** Tested email sending
  - Password reset email ✓
  - Or manual email in admin

- [ ] **9.2** Tested payment flow
  - Razorpay button visible ✓
  - Test payment with Razorpay test keys

- [ ] **9.3** Monitored performance
  - Checked Koyeb metrics
  - Memory usage: normal ✓
  - CPU usage: normal ✓

- [ ] **9.4** Set up backups (Optional)
  - Plan: Download db.sqlite3 weekly
  - Or: Use GitHub Actions for automation

---

## Phase 10: Production Ready

- [ ] **10.1** Verified settings
  - DEBUG = False ✓
  - SECRET_KEY is strong ✓
  - ALLOWED_HOSTS correct ✓
  - SSL enabled (HTTPS) ✓

- [ ] **10.2** Shared with team
  - Production URL: `https://fitzone-yourname-xxxx.koyeb.app`
  - Admin: `https://fitzone-yourname-xxxx.koyeb.app/admin/`
  - Credentials: Shared securely

- [ ] **10.3** Documented deployment
  - Saved deployment date
  - Noted Koyeb service name
  - Saved admin credentials securely

- [ ] **10.4** Planned maintenance
  - Monitor logs daily for first week
  - Set up alerts (optional)
  - Plan backup schedule

---

## 🎉 Deployment Complete!

**Production URL:** `https://fitzone-yourname-xxxx.koyeb.app`  
**Admin URL:** `https://fitzone-yourname-xxxx.koyeb.app/admin/`  
**Deployment Date:** ________________  
**Status:** ✅ LIVE

---

## Important Credentials

| Item | Value | Location |
|---|---|---|
| Admin Username | `admin` | Use for login |
| Admin Password | `admin123` | Secure storage |
| SECRET_KEY | (long string) | Koyeb env var |
| Gmail Password | (app password) | Koyeb env var |
| Razorpay Keys | (test/live) | Koyeb env var |

**Keep these safe!** Never commit to GitHub.

---

## Troubleshooting Checklist

If something fails, check:

- [ ] Service shows **"Running"** in Koyeb
- [ ] Environment variables all set
- [ ] **No 404 errors** on CSS/JS
- [ ] **No "DisallowedHost"** errors
- [ ] **Database migrations** applied
- [ ] **Email credentials** correct
- [ ] **Razorpay keys** valid

If still broken, check **KOYEB_DEPLOYMENT_GUIDE.md** Troubleshooting section.

---

**Next Steps After Deployment:**

1. Share production URL with users
2. Monitor logs daily (first week)
3. Perform user acceptance testing
4. Set up scheduled backups
5. Plan for future upgrades

**Your FitZone app is now LIVE on Koyeb! 🚀**


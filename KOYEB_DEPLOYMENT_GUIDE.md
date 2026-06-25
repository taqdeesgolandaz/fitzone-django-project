# 🚀 FitZone Koyeb Deployment Guide - Free Plan

**Status:** Ready for Deployment  
**Platform:** Koyeb (Free Tier)  
**Database:** SQLite3  
**Python:** 3.11  
**Domain:** `fitzone-yourname.koyeb.app`  
**Cost:** FREE! ✨

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Prepare Local Environment](#step-1-prepare-local-environment)
3. [Step 2: Verify Deployment Files](#step-2-verify-deployment-files)
4. [Step 3: Push to GitHub](#step-3-push-to-github)
5. [Step 4: Create Koyeb Account](#step-4-create-koyeb-account)
6. [Step 5: Deploy from GitHub](#step-5-deploy-from-github)
7. [Step 6: Configure Environment Variables](#step-6-configure-environment-variables)
8. [Step 7: Test Your App](#step-7-test-your-app)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- ✅ GitHub account with code pushed
- ✅ Production SECRET_KEY generated
- ✅ Gmail account with app password
- ✅ Razorpay test/live keys
- ✅ Koyeb account (free)

---

## Step 1: Prepare Local Environment

### 1.1 Generate Production SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Save the output** - you'll need it for Koyeb environment variables.

### 1.2 Test Locally

```bash
cd "c:\Users\GLOBAL T\Desktop\FitZone"
myenv\Scripts\activate
python manage.py runserver
```

Visit `http://127.0.0.1:8000` and verify everything works.

Press `Ctrl+C` to stop.

---

## Step 2: Verify Deployment Files

These files were automatically created for Koyeb:

- ✅ `Dockerfile` - Container configuration
- ✅ `Procfile` - Application startup command
- ✅ `docker-compose.yml` - Local Docker testing (optional)
- ✅ `.dockerignore` - Files to exclude from container
- ✅ `requirements.txt` - All dependencies (already present)
- ✅ `manage.py` - Django management (already present)

**No changes needed!** Everything is ready.

---

## Step 3: Push to GitHub

Make sure all code is committed:

```bash
cd "c:\Users\GLOBAL T\Desktop\FitZone"
git status
```

If there are uncommitted changes:

```bash
git add .
git commit -m "Add Koyeb deployment configuration"
git push origin main
```

---

## Step 4: Create Koyeb Account

1. Go to: **https://www.koyeb.com**
2. Click **"Sign Up for free"**
3. Create account with GitHub (easiest option)
   - Authorize Koyeb to access your GitHub
   - Select **Public or Private** repositories
4. Verify email
5. You're in! ✨

---

## Step 5: Deploy from GitHub

### 5.1 Create New Service

1. In Koyeb Dashboard, click **"Create Service"** or **"Deploy"**
2. Select **"GitHub"** as source
3. Choose your repository: `fitzone-django-project`
4. Select branch: `main`

### 5.2 Configure Deployment

| Setting | Value |
|---|---|
| **Builder** | Dockerfile |
| **Port** | 8000 |
| **HTTP Port** | 8000 |
| **Name** | `fitzone-app` (or custom name) |

### 5.3 Environment Variables

Click **"Add Environment Variable"** for each:

| Variable | Value |
|---|---|
| `DEBUG` | `False` |
| `SECRET_KEY` | `(your-generated-key)` |
| `ALLOWED_HOSTS` | `*.koyeb.app,localhost,127.0.0.1` |
| `DATABASE_URL` | (leave empty - uses SQLite) |
| `EMAIL_HOST_USER` | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `your-16-char-app-password` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `DEFAULT_FROM_EMAIL` | `FitZone <your-email@gmail.com>` |
| `SERVER_EMAIL` | `your-email@gmail.com` |
| `RAZORPAY_KEY_ID` | `rzp_test_SwU8wO2DuOpWoo` (or live key) |
| `RAZORPAY_KEY_SECRET` | `hS7jKWDqXYQRbo3IoS6J3oMB` (or live secret) |
| `SITE_URL` | `https://fitzone-yourname.koyeb.app` |

### 5.4 Deploy

Click **"Deploy"** and wait 2-5 minutes.

Monitor progress in the **"Activity"** tab.

---

## Step 6: Verify Deployment

### 6.1 Check Deployment Status

- ✅ In Koyeb Dashboard, service should show **"Running"** (green)
- ✅ **"Replicas"** should show `1/1`
- ✅ **"Build logs"** should show no errors

### 6.2 Get Your URL

In Koyeb Dashboard:
- Find your service
- Copy the **Public URL** (format: `https://fitzone-yourname-xxxx.koyeb.app`)
- This is your live app!

---

## Step 7: Test Your App

### 7.1 Access Homepage

Visit your public URL in browser:
```
https://fitzone-yourname-xxxx.koyeb.app
```

Expected: FitZone homepage loads ✓

### 7.2 Access Admin Panel

```
https://fitzone-yourname-xxxx.koyeb.app/admin/
```

Login with:
- **Username:** `admin`
- **Password:** `admin123`

Expected: Django admin interface ✓

### 7.3 Check CSS/JS Loading

- Open browser console (F12)
- Check for 404 errors
- Page should be styled (not plain HTML)

### 7.4 Test User Registration

- Go to registration page
- Create a test account
- Verify email sends (check spam folder)

---

## Auto-Deploy from GitHub

**Great news:** Koyeb automatically redeploys when you push to GitHub!

To update production:

```bash
cd "c:\Users\GLOBAL T\Desktop\FitZone"
# Make code changes
git add .
git commit -m "Update feature XYZ"
git push origin main
# Koyeb automatically deploys! 🚀
```

Monitor deployment in Koyeb Dashboard.

---

## Troubleshooting

### Issue: Service shows "Failed" or "Crashed"

**Solution:** Check build logs
1. Click on service
2. Go to **"Logs"** tab
3. Look for error messages
4. Common issues:
   - Missing environment variable
   - Syntax error in code
   - Database migration failed

### Issue: 404 "Not Found" on Homepage

**Solution:** Check logs for errors
```
https://fitzone-yourname-xxxx.koyeb.app/
```

If you see error:
- Service logs will show the issue
- Fix locally, commit, push
- Koyeb redeploys automatically

### Issue: "DisallowedHost" Error

**Solution:** Check ALLOWED_HOSTS environment variable
- Should be: `*.koyeb.app,localhost,127.0.0.1`
- Update in Koyeb Dashboard → Environment Variables
- Redeploy service

### Issue: Email Not Sending

**Solution:** Verify Gmail credentials
1. Go to: https://myaccount.google.com/apppasswords
2. Generate new app password
3. Update EMAIL_HOST_PASSWORD in Koyeb
4. Redeploy

### Issue: Static Files Not Loading (CSS/JS 404)

**Solution:** Rebuild Docker image
1. In Koyeb, go to service settings
2. Click **"Rebuild and redeploy"**
3. Wait for deployment to complete

### Issue: Database Locked or Migration Failed

**Solution:** 
1. Koyeb Console → SSH into container
2. Run:
```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```
3. Redeploy

---

## Monitoring & Logs

### View Live Logs

In Koyeb Dashboard:
1. Click your service
2. Go to **"Logs"** tab
3. See real-time application output
4. Filter by error messages

### View Deployment Status

- **"Activity"** tab shows deployment history
- See build progress and any errors
- Rollback to previous version if needed

---

## Scaling (If Needed Later)

Free tier Koyeb includes:
- 1 service running 24/7
- Automatic scaling off
- 512MB memory limit

If you need more power:
- Upgrade to Koyeb **Standard** tier (~$5/month)
- Get more memory, CPU, and replicas

---

## Performance Tips

### For Free Tier:

1. **Use SQLite** (already configured) ✓
2. **Limit database queries** in views
3. **Cache static files** (WhiteNoise handles this) ✓
4. **Use CDN** for large media files (optional)
5. **Monitor logs** regularly

### Optimize Queries:

Add `.select_related()` and `.prefetch_related()` in views:
```python
# Good
users = CustomUser.objects.select_related('membership').all()

# Avoid
users = CustomUser.objects.all()  # N+1 queries
```

---

## Security Checklist

Before going to production:

- [ ] `DEBUG = False` ✓
- [ ] Strong `SECRET_KEY` ✓
- [ ] `ALLOWED_HOSTS` configured ✓
- [ ] Email credentials secure ✓
- [ ] Razorpay keys production-ready
- [ ] `.env` file NOT in GitHub (.gitignore) ✓
- [ ] HTTPS enabled (Koyeb provides free SSL) ✓
- [ ] Database backups planned

---

## Database Backups

Since you're using SQLite:

1. **In Koyeb Console:**
```bash
# Download database
python manage.py dumpdata > backup.json
```

2. **Or use local machine:**
```bash
# Connect to Koyeb service
koyeb files download db.sqlite3
```

3. **Or automate (Advanced):**
   - Use GitHub Actions to backup daily
   - Store backups in GitHub Releases

---

## Next Steps

1. ✅ Complete Steps 1-7 above
2. ✅ Test all features thoroughly
3. ✅ Monitor logs for errors
4. ✅ Set up backups
5. ✅ Plan future updates

---

## Support & Documentation

- **Koyeb Docs:** https://docs.koyeb.com
- **Django Docs:** https://docs.djangoproject.com
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **Razorpay Integration:** https://razorpay.com/docs

---

## Summary

| Item | Status |
|---|---|
| **Platform** | Koyeb (FREE) |
| **Database** | SQLite3 |
| **Python** | 3.11 |
| **Deployment** | GitHub → Koyeb (Auto) |
| **Domain** | `*.koyeb.app` (FREE) |
| **SSL/HTTPS** | ✅ Included |
| **Cost** | FREE! 🎉 |

---

**Your FitZone app is ready to deploy! 🚀**

Follow the steps above and your app will be live in minutes!

Questions? Check Troubleshooting section or Koyeb docs.


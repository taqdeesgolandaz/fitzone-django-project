# FitZone Render Deployment Guide

This guide will walk you through deploying FitZone to Render, a modern cloud platform for web applications.

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Account**: Your code must be in a GitHub repository
3. **Git**: Installed and configured
4. **Python 3.11+**: Installed locally for testing

## Pre-Deployment Setup

### 1. Generate Django Secret Key

Generate a new SECRET_KEY for production:

```bash
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

Copy this key for later use.

### 2. Prepare Your Razorpay Keys

Decide whether to use:
- **Test Keys** (for development): `rzp_test_*`
- **Live Keys** (for production): `rzp_live_*`

Get these from your Razorpay dashboard.

### 3. Email Configuration

For Gmail specifically:
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use this app password (NOT your regular password) as `EMAIL_HOST_PASSWORD`

For other email providers:
- Use your mail server's SMTP settings
- Some providers require app-specific passwords

### 4. Update GitHub Repository

Ensure your repository is up to date:

```bash
git add -A
git commit -m "Prepare for Render deployment"
git push origin main
```

**Important**: Do NOT commit your `.env` file. It's already in `.gitignore`.

## Deployment Steps

### Step 1: Connect Render to GitHub

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"Web Service"**
3. Select **"Deploy an existing repository"**
4. Authorize Render to access your GitHub account
5. Select your FitZone repository

### Step 2: Configure Your Web Service

1. **Name**: `fitzone` (or your preferred name)
2. **Environment**: Python
3. **Region**: Choose closest to your users (Oregon, Ohio, Frankfurt, etc.)
4. **Branch**: `main` (or your deployment branch)
5. **Build Command**: (Will be read from render.yaml)
6. **Start Command**: (Will be read from render.yaml)
7. **Plan**: Select appropriate tier (Starter for testing, Standard for production)

### Step 3: Create PostgreSQL Database

1. In Render Dashboard, click **"New"** → **"PostgreSQL"**
2. **Name**: `fitzone-db`
3. **Database**: `fitzone`
4. **User**: Leave as default
5. **Region**: Same as your web service
6. **Plan**: Starter (can upgrade later)
7. Click **"Create Database"**

### Step 4: Connect Database to Web Service

After the database is created:

1. Go to your FitZone web service
2. Click **"Environment"**
3. Add `DATABASE_URL` variable - Render will automatically populate this when you link the database

Or manually set it from the PostgreSQL database page:
- Copy the connection string from the database details
- Add it as `DATABASE_URL` environment variable

### Step 5: Set Environment Variables

In your Render Dashboard, go to your web service and click **"Environment"**. Add these variables:

```
DEBUG=false
SECRET_KEY=<your-generated-secret-key-from-step-1>
ALLOWED_HOSTS=your-app-name.onrender.com,localhost
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_HOST_USER=fitzone.alerts@gmail.com
EMAIL_HOST_PASSWORD=<your-app-password>
DEFAULT_FROM_EMAIL=FitZone <fitzone.alerts@gmail.com>
SERVER_EMAIL=fitzone.alerts@gmail.com
RAZORPAY_KEY_ID=<your-razorpay-key>
RAZORPAY_KEY_SECRET=<your-razorpay-secret>
SITE_URL=https://your-app-name.onrender.com
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=true
SECURE_HSTS_PRELOAD=true
```

### Step 6: Configure Email for OAuth/Allauth

If using OAuth providers (Google, Facebook, Apple):

1. Go to your Django admin panel: `https://your-app.onrender.com/admin`
2. Navigate to **Sites** → **Edit the default site**
3. Set Domain to: `your-app-name.onrender.com`
4. Set Display Name: `FitZone`
5. Save

This ensures OAuth redirects work correctly.

### Step 7: Deploy

1. In Render Dashboard, go to your web service
2. Click **"Manual Deploy"** or **"Redeploy"**
3. Render will:
   - Install dependencies from `requirements.txt`
   - Run migrations: `python manage.py migrate`
   - Collect static files: `python manage.py collectstatic --noinput`
   - Start gunicorn server

Wait for deployment to complete (usually 5-10 minutes).

## Verify Deployment

### 1. Check Service Status

- Go to Render Dashboard
- Your service should show "Live" status
- Click the URL to visit your app

### 2. Access Admin Panel

1. Visit `https://your-app-name.onrender.com/admin`
2. Log in with your Django superuser credentials
3. Verify database is working

### 3. Check Logs

- In Render Dashboard, click "Logs" to see deployment and runtime logs
- Look for any error messages

### 4. Test Core Features

- Test user registration
- Test login
- Test payment flows (use Razorpay test keys)
- Check static files load (CSS, JavaScript, images)

## Troubleshooting

### Static Files Not Loading

**Problem**: CSS/images not showing

**Solution**:
1. Run manual migration: `render/deploy.sh` (if available)
2. Trigger rebuild from Render dashboard
3. Check if `STATICFILES_STORAGE` is properly set in settings.py

### Database Connection Error

**Problem**: "Cannot connect to PostgreSQL"

**Solution**:
1. Verify DATABASE_URL is set in environment variables
2. Check the database is running (Render dashboard → PostgreSQL)
3. Ensure firewall rules allow connections (Render auto-configures this)

### 502 Bad Gateway

**Problem**: Service returns 502 error

**Solution**:
1. Check logs for errors: `python manage.py migrate` failures
2. Verify all environment variables are set
3. Check SECRET_KEY and other critical variables
4. Restart service: Render dashboard → "Restart"

### Email Not Sending

**Problem**: Emails not being delivered

**Solutions**:
- Verify `EMAIL_HOST_PASSWORD` is an app-specific password (for Gmail)
- Check email logs: Django admin → Logs (if using database backend)
- Use SMTP debugging: Add `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` temporarily

### Razorpay Integration Issues

**Problem**: Payment gateway not working

**Solution**:
- Verify `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in environment
- Check Razorpay account is activated for test mode
- Ensure keys match your Razorpay dashboard

## Updating Your Application

### Deploy Updates

```bash
# Make your changes locally
git add -A
git commit -m "Your update message"
git push origin main
```

Render automatically redeploys when you push to your branch (if auto-deploy is enabled).

### Manual Database Migrations

After deploying with model changes:

1. Go to Render Dashboard → Your web service
2. Click "Shell" to open a bash shell
3. Run: `python manage.py migrate`

### Collect Static Files

If static files are missing after update:

1. In the Shell, run: `python manage.py collectstatic --noinput`
2. Restart the service

## Going Live with Razorpay

When ready for production payments:

1. Complete Razorpay merchant verification
2. Get live Razorpay keys: `rzp_live_*`
3. Update environment variables:
   - `RAZORPAY_KEY_ID=rzp_live_YOUR_LIVE_KEY`
   - `RAZORPAY_KEY_SECRET=YOUR_LIVE_SECRET`
4. Test thoroughly with small amounts
5. Monitor transaction logs in Razorpay dashboard

## Performance Optimization

### Render Plans

- **Starter**: Good for testing, free tier. Limited resources.
- **Standard**: Recommended for production with decent traffic
- **Pro/Premium**: For high-traffic applications

### Database Optimization

- Enable connection pooling in PostgreSQL
- Use indexing for frequently queried fields
- Consider caching strategy (Redis on Render)

### CDN for Static/Media Files

Consider using Render's built-in or external CDN:
- Render Blob Storage
- Cloudflare
- AWS S3

## Monitoring and Maintenance

### Monitor Logs

```bash
# View recent logs in Dashboard
Render Dashboard → Web Service → Logs
```

### Health Checks

Render automatically checks if your app is running:
- Configure health check endpoint in service settings
- Default: GET request to root URL

### Backup Database

Set up automatic PostgreSQL backups:
- Render Dashboard → PostgreSQL → Backups
- Configure retention period

## Support and Resources

- [Render Documentation](https://render.com/docs)
- [Django Deployment Guide](https://docs.djangoproject.com/en/5.0/howto/deployment/)
- [Razorpay Integration Docs](https://razorpay.com/docs/)
- [Email Configuration Guide](https://docs.djangoproject.com/en/5.0/topics/email/)

## Rollback

If something goes wrong:

1. Go to Render Dashboard → Your service
2. Click "Deployments"
3. Select a previous successful deployment
4. Click "Redeploy"

Your app will revert to the previous version while you fix issues.

---

**Questions?** Check the logs in Render Dashboard first, then consult the resources above.

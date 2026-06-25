# FitZone Render Deployment Checklist

Use this checklist before deploying to Render.

## Pre-Deployment (Local)

- [ ] Update Django SECRET_KEY for production
  ```bash
  python manage.py shell
  >>> from django.core.management.utils import get_random_secret_key
  >>> print(get_random_secret_key())
  ```

- [ ] Test application locally with PostgreSQL (optional but recommended)
  ```bash
  python manage.py runserver
  ```

- [ ] Verify all environment variables are documented in `.env.example`

- [ ] Test with DEBUG=False locally:
  ```bash
  DEBUG=false python manage.py runserver
  ```

- [ ] Run migrations:
  ```bash
  python manage.py migrate
  ```

- [ ] Collect static files:
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] Commit and push to GitHub:
  ```bash
  git add -A
  git commit -m "Prepare for Render deployment"
  git push origin main
  ```

## Render Dashboard Setup

### Web Service
- [ ] Create web service from GitHub repository
- [ ] Set Python 3.11 as runtime
- [ ] Render will read `render.yaml` automatically

### PostgreSQL Database
- [ ] Create PostgreSQL database
- [ ] Note: Render auto-links DATABASE_URL if configured in render.yaml
- [ ] Database region matches web service region

### Environment Variables
Set all of these in Render dashboard (Web Service → Environment):

**Django Core:**
- [ ] `DEBUG=false`
- [ ] `SECRET_KEY=<your-generated-key>`
- [ ] `ALLOWED_HOSTS=your-app-name.onrender.com,localhost`

**Database:**
- [ ] `DATABASE_URL` (auto-set if using render.yaml)

**Email:**
- [ ] `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- [ ] `EMAIL_HOST=<smtp.mailgun.org or your provider>`
- [ ] `EMAIL_PORT=465`
- [ ] `EMAIL_USE_SSL=true`
- [ ] `EMAIL_USE_TLS=false`
- [ ] `EMAIL_HOST_USER=<your-mail-provider-username>`
- [ ] `EMAIL_HOST_PASSWORD=<your-mail-provider-password>`
- [ ] `DEFAULT_FROM_EMAIL=<email>`
- [ ] `SERVER_EMAIL=<email>`

**Razorpay:**
- [ ] `RAZORPAY_KEY_ID=<test-or-live-key>`
- [ ] `RAZORPAY_KEY_SECRET=<test-or-live-secret>`

**Security (Production):**
- [ ] `SECURE_SSL_REDIRECT=true`
- [ ] `SESSION_COOKIE_SECURE=true`
- [ ] `CSRF_COOKIE_SECURE=true`
- [ ] `SECURE_HSTS_SECONDS=31536000`
- [ ] `SECURE_HSTS_INCLUDE_SUBDOMAINS=true`
- [ ] `SECURE_HSTS_PRELOAD=true`

**Site:**
- [ ] `SITE_URL=https://your-app-name.onrender.com`

## First Deployment

- [ ] Click "Deploy" in Render dashboard
- [ ] Monitor logs: Dashboard → Logs
- [ ] Wait for deployment to complete (5-10 minutes)
- [ ] Check service status shows "Live"

## Post-Deployment Verification

- [ ] Application loads without 502 errors
- [ ] Access admin panel: `/admin/`
- [ ] Log in with superuser account
- [ ] Check static files load (CSS, images, JavaScript)
- [ ] Test user registration
- [ ] Test login functionality
- [ ] Verify email sending (check logs if failed)
- [ ] Test payment flow with test Razorpay keys

### Database Verification
In Render Shell:
```bash
python manage.py showmigrations
python manage.py dbshell
SELECT * FROM accounts_customuser LIMIT 1;
\q
exit
```

## If Issues Occur

- [ ] Check logs in Render dashboard
- [ ] Verify all environment variables are set
- [ ] Verify DATABASE_URL format matches `postgres://user:pass@host:port/dbname`
- [ ] Check SECRET_KEY is strong and properly set
- [ ] Verify Razorpay keys are correct
- [ ] Test email configuration separately
- [ ] Restart service: Dashboard → "Restart"
- [ ] Manual redeploy: Dashboard → "Manual Deploy"

## Going Live (Razorpay)

When ready for real payments:

- [ ] Get live Razorpay keys from dashboard
- [ ] Update environment variables:
  - `RAZORPAY_KEY_ID=rzp_live_YOUR_KEY`
  - `RAZORPAY_KEY_SECRET=YOUR_SECRET`
- [ ] Test with small transaction amount
- [ ] Monitor Razorpay dashboard for transactions

## Ongoing Maintenance

- [ ] Monitor Render logs daily
- [ ] Check database storage usage (PostgreSQL)
- [ ] Set up automated backups for PostgreSQL
- [ ] Monitor for error rates in application logs
- [ ] Keep dependencies updated regularly

## Useful Render Shell Commands

```bash
# Check Python version
python --version

# Test Django settings
python manage.py check

# See database migrations status
python manage.py showmigrations

# List environment variables
env | grep -i django

# Check disk usage
df -h

# View logs
tail -f /var/log/syslog
```

---

**Deployment Status:**
- [ ] Development environment tested
- [ ] GitHub pushed with all changes
- [ ] Render service created
- [ ] Database configured
- [ ] Environment variables set
- [ ] Initial deployment successful
- [ ] All verification steps passed
- [ ] Ready for production traffic


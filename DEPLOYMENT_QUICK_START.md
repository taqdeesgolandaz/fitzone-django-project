# 🚀 FitZone Deployment - Quick Start Guide

**Ready to deploy your FitZone app to PythonAnywhere? Start here!**

---

## What's Been Prepared For You

✅ **PYTHONANYWHERE_DEPLOYMENT_GUIDE.md** - Complete 12-step deployment guide  
✅ **PYTHONANYWHERE_CHECKLIST.md** - Track your progress  
✅ **.env.production** - Template for production variables  
✅ **requirements.txt** - All dependencies ready  
✅ **fitzone/settings.py** - Pre-configured for production  
✅ **fitzone/wsgi.py** - Ready to use  
✅ **.gitignore** - Prevents committing secrets  

---

## 5-Minute Quick Start

### 1️⃣ Create Production SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output.

### 2️⃣ Create Local .env File

Create `c:\Users\GLOBAL T\Desktop\FitZone\.env` with:

```
DEBUG=False
SECRET_KEY=<paste_your_generated_key_here>
ALLOWED_HOSTS=YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
RAZORPAY_KEY_ID=rzp_test_SwU8wO2DuOpWoo
RAZORPAY_KEY_SECRET=hS7jKWDqXYQRbo3IoS6J3oMB
```

### 3️⃣ Push to GitHub

```bash
cd c:\Users\GLOBAL T\Desktop\FitZone
git add .
git commit -m "Prepare for PythonAnywhere deployment"
git push origin main
```

### 4️⃣ Go to PythonAnywhere

1. Sign up: https://www.pythonanywhere.com
2. Create web app (Python 3.10)
3. Clone your GitHub repo in console
4. Install requirements
5. Follow PYTHONANYWHERE_DEPLOYMENT_GUIDE.md

### 5️⃣ Set Environment Variables

In PythonAnywhere Web App settings → Environment variables, add each variable.

---

## Critical Information

| Item | Your Value | Notes |
|---|---|---|
| **PythonAnywhere Username** | ________________ | Will be: `username.pythonanywhere.com` |
| **Production Secret Key** | (generated above) | Keep SECRET! Change before deploying |
| **Gmail Address** | ________________ | For email notifications |
| **Gmail App Password** | ________________ | Generate at myaccount.google.com/apppasswords |
| **Razorpay Key ID** | rzp_test_xxx | Test key: rzp_test_SwU8wO2DuOpWoo |
| **Razorpay Key Secret** | hS7jKWDqXYQRbo3IoS6J3oMB | From Razorpay dashboard |
| **Superuser Username** | ________________ | For admin access |
| **Superuser Password** | ________________ | Save securely! |

---

## File Overview

```
PYTHONANYWHERE_DEPLOYMENT_GUIDE.md
├─ Step 1: Prepare Local Environment
├─ Step 2: Push to GitHub
├─ Step 3: Set Up PythonAnywhere Account
├─ Step 4: Clone Project
├─ Step 5: Configure Virtual Environment
├─ Step 6: Configure Django Settings
├─ Step 7: Set Up Static Files
├─ Step 8: Create WSGI Configuration
├─ Step 9: Configure Environment Variables
├─ Step 10: Initialize Database
├─ Step 11: Set Up Static Files Mapping
├─ Step 12: Reload Web App
└─ Testing & Troubleshooting

PYTHONANYWHERE_CHECKLIST.md
├─ 14 phases with checkboxes
├─ Verification commands
└─ Final deployment confirmation
```

---

## Common Tasks

### Generate Production Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Test Project Locally

```bash
source myenv/Scripts/activate
python manage.py runserver
# Visit http://127.0.0.1:8000
```

### Push Changes to GitHub

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

### Deploy to PythonAnywhere

1. Clone: `git clone https://github.com/YOUR_USERNAME/fitzone.git fitzone-django-project`
2. Virtual env: `mkvirtualenv --python=/usr/bin/python3.10 fitzone`
3. Install: `pip install -r requirements.txt`
4. Migrate: `python manage.py migrate`
5. Static: `python manage.py collectstatic --noinput`
6. Reload web app ✓

---

## Troubleshooting

### Website Shows "DisallowedHost"
→ Update ALLOWED_HOSTS in environment variables

### CSS/JS Not Loading (404 errors)
→ Run `python manage.py collectstatic --noinput` and reload

### Email Not Sending
→ Check EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, and Gmail app password

### 500 Server Errors
→ Check error logs: `/var/log/username.pythonanywhere.com.error.log`

---

## Next Steps

1. ✅ Read **PYTHONANYWHERE_DEPLOYMENT_GUIDE.md** (15 min read)
2. ✅ Gather your credentials (Gmail, Razorpay, etc.)
3. ✅ Create PythonAnywhere account
4. ✅ Push code to GitHub
5. ✅ Follow the 12-step deployment guide
6. ✅ Use **PYTHONANYWHERE_CHECKLIST.md** to track progress
7. ✅ Test your live site
8. ✅ Celebrate! 🎉

---

## Support

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Django Docs:** https://docs.djangoproject.com/en/5.0/
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **Razorpay Dashboard:** https://dashboard.razorpay.com/

---

## ⏱️ Estimated Time to Deploy

- **Preparation:** 10-15 minutes
- **GitHub Setup:** 5 minutes
- **PythonAnywhere Setup:** 15-20 minutes
- **Running Migrations:** 5 minutes
- **Testing:** 10 minutes
- **Total:** ~45-50 minutes

**Let's get your app live! 🚀**

---

**Questions?** Follow the detailed guide: **PYTHONANYWHERE_DEPLOYMENT_GUIDE.md**

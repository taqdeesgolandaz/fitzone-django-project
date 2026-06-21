"""
Django settings for fitzone project.
"""

from pathlib import Path
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here-change-this-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*', '10.231.81.210', 'localhost', '127.0.0.1']

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'support',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.apple',
    
    # Local apps
    'accounts',
    'membership',
    'payments',
    'workouts',
    'diet',
    'tracking',
    'trainers',
    'notifications',
    'admin_dashboard',
    'achievements',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.SingleSessionMiddleware',  # Add this (we'll create it)
]

ROOT_URLCONF = 'fitzone.urls'



WSGI_APPLICATION = 'fitzone.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Supported languages for the application
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'Hindi'),
    ('ta', 'Tamil'),
    ('te', 'Telugu'),
]

# Where to store translation files
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
SITE_ID = 1

ACCOUNT_EMAIL_VERIFICATION = 'none'
# Use new allauth config keys to avoid deprecation warnings
# `ACCOUNT_LOGIN_METHOD` is a single string: 'username', 'email' or 'username_email'
ACCOUNT_LOGIN_METHOD = 'username_email'
ACCOUNT_SIGNUP_FIELDS = ['email', 'username', 'password1', 'password2']
# `ACCOUNT_EMAIL_REQUIRED` is deprecated; rely on `ACCOUNT_SIGNUP_FIELDS` instead
SOCIALACCOUNT_QUERY_EMAIL = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'FIELDS': ['id', 'email', 'name', 'first_name', 'last_name'],
    },
    'apple': {
        'SCOPE': ['name', 'email'],
    },
}

# Razorpay Configuration (Test Keys)
# Note: UPI apps (GPay, PhonePe, Paytm) appear only in LIVE MODE
RAZORPAY_KEY_ID = 'rzp_test_SwU8wO2DuOpWoo'
RAZORPAY_KEY_SECRET = 'hS7jKWDqXYQRbo3IoS6J3oMB'

# UPI Payment Settings
UPI_ID = '8177845613@kotakbank'
UPI_PAYEE_MOBILE = '8177845613'
ACCOUNT_NUMBER = '9748972808'
IFSC_CODE = 'KKBK0001980'
BANK_NAME = 'Kotak Mahindra Bank'
BRANCH_NAME = 'MAHARANA PRATAP NAGAR'
UPI_APPS = ['Google Pay', 'PhonePe', 'Paytm', 'BHIM']
UPI_PAYEE_NAME = 'FitZone'

# For Live Mode (to see GPay, PhonePe, Paytm buttons):
# RAZORPAY_KEY_ID = 'rzp_live_YourLiveKeyHere'
# RAZORPAY_KEY_SECRET = 'YourLiveSecretHere'

# Login URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'fitzone.alerts@gmail.com'
EMAIL_HOST_PASSWORD = 'yaci rqpy yelr woqv'
DEFAULT_FROM_EMAIL = 'FitZone <fitzone.alerts@gmail.com>'
SERVER_EMAIL = 'fitzone.alerts@gmail.com'
EMAIL_SUBJECT_PREFIX = '[FitZone] '

# Add these for better deliverability
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 30
SITE_URL = 'http://10.198.213.210:8000'

# Templates (required for admin and django templates)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

"""
Django settings for fitzone project.
"""

from pathlib import Path
import os
from datetime import timedelta
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file (for local development)
from dotenv import load_dotenv
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '10.96.118.210',
    '10.15.136.210',
    '.onrender.com',  # Render deployment
    'fitzone.onrender.com',  # Your specific Render domain
]

# Add Render's external hostname dynamically, if available
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    ALLOWED_HOSTS.append(f'.{RENDER_EXTERNAL_HOSTNAME}')

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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
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
# Use DATABASE_URL if available (Render), otherwise use SQLite locally
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
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

# WhiteNoise Configuration for serving static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
# allauth login/signup settings
# Preferred new config: specify allowed login identifiers as a set
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
# Signup fields should list only profile fields; passwords are handled by forms separately.
# Mark required fields with a trailing '*' so allauth recognizes required signup fields.
# Ensure at least one of the ACCOUNT_LOGIN_METHODS is present and required here.
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username']
# Keep backward-compatible single-key for templates/etc. (optional)
ACCOUNT_LOGIN_METHOD = 'username_email'
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

# Razorpay Configuration
# Use environment variables - set in .env for local development, in Render dashboard for production
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_SwU8wO2DuOpWoo')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'hS7jKWDqXYQRbo3IoS6J3oMB')

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
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'fitzone.alerts@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'FitZone <fitzone.alerts@gmail.com>')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'fitzone.alerts@gmail.com')
EMAIL_SUBJECT_PREFIX = '[FitZone] '

# Add these for better deliverability
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'false').lower() in ['true', '1', 'yes']
EMAIL_TIMEOUT = 30
SITE_URL = os.getenv('SITE_URL')

# Safety fallback for local development: if SMTP backend is configured but no
# `EMAIL_HOST_PASSWORD` is set, switch to the console backend to avoid
# SMTP authentication errors while testing locally.
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend' and not EMAIL_HOST_PASSWORD:
    print('WARNING: EMAIL_HOST_PASSWORD is not set. Falling back to console email backend for local development.')
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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

# Security Settings for Production
if not DEBUG:
    # HTTPS and Security Headers
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'false').lower() in ['true', '1', 'yes']
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true').lower() in ['true', '1', 'yes']
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'true').lower() in ['true', '1', 'yes']
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        "default-src": ("'self'",),
        "script-src": ("'self'", "'unsafe-inline'"),
        "style-src": ("'self'", "'unsafe-inline'"),
    }
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'true').lower() in ['true', '1', 'yes']
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'true').lower() in ['true', '1', 'yes']
    
    # Content Security
    X_FRAME_OPTIONS = 'DENY'

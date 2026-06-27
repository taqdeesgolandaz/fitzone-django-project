"""
Django settings for fitzone project.
"""

from pathlib import Path
import os
import sys
from datetime import timedelta
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file (for local development)
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'fitzone-application.onrender.com',
    '.onrender.com',
]

# If DEBUG is True, allow all hosts
if DEBUG:
    ALLOWED_HOSTS = ['*']

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

CLOUDINARY_APPS = []
try:
    import cloudinary  # noqa: F401
    import cloudinary_storage  # noqa: F401
    CLOUDINARY_APPS = ['cloudinary', 'cloudinary_storage']
except ImportError:
    print('Cloudinary packages not installed; falling back to local file storage.', file=sys.stderr)

INSTALLED_APPS += CLOUDINARY_APPS

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
# Use DATABASE_URL if available, otherwise use SQLite locally
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

# Cloudinary storage for production media uploads
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL', '')
USE_CLOUDINARY = bool(CLOUDINARY_URL or os.environ.get('CLOUDINARY_CLOUD_NAME'))

if USE_CLOUDINARY:
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api

        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
            'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
            'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
        }

        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
        )

        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    except ImportError as exc:
        print(f'Cloudinary package not installed: {exc}. Falling back to local file storage.', file=sys.stderr)
        DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

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
# Use environment variables - set in .env for local development and production
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '').strip()
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '').strip()

if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    print('WARNING: Razorpay keys are not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in the environment.', file=sys.stderr)

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

import os

# Email Configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp-relay.brevo.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() in ['true', '1', 'yes']
if EMAIL_USE_SSL and EMAIL_USE_TLS:
    EMAIL_USE_TLS = False
    print('WARNING: EMAIL_USE_SSL and EMAIL_USE_TLS both enabled; using SSL only.', file=sys.stderr)

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'aff029001')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', os.environ.get('BREVO_SMTP_PASSWORD', ''))

# Brevo API Settings
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
BREVO_SENDER_EMAIL = os.environ.get('BREVO_SENDER_EMAIL', 'fitzone.alerts@gmail.com')
BREVO_SENDER_NAME = os.environ.get('BREVO_SENDER_NAME', 'FitZone')
USE_BREVO_API = bool(BREVO_API_KEY)

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'FitZone <fitzone.alerts@gmail.com>')
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '10'))
SITE_URL = os.environ.get('SITE_URL', '')

if not DEBUG and not EMAIL_HOST_PASSWORD:
    print('ERROR: EMAIL_HOST_PASSWORD is not set in production environment. Emails will fail to send.', file=sys.stderr)

print(
    'EMAIL CONFIG:',
    f'BACKEND={EMAIL_BACKEND}',
    f'HOST={EMAIL_HOST}',
    f'PORT={EMAIL_PORT}',
    f'TLS={EMAIL_USE_TLS}',
    f'SSL={EMAIL_USE_SSL}',
    f'FROM={DEFAULT_FROM_EMAIL}',
    f'USER_SET={bool(EMAIL_HOST_USER)}',
    f'PASSWORD_SET={bool(EMAIL_HOST_PASSWORD)}',
    f'BREVO_API_KEY_SET={bool(BREVO_API_KEY)}',
    f'BREVO_SENDER_EMAIL={BREVO_SENDER_EMAIL}',
    f'DEFAULT_FROM_EMAIL={DEFAULT_FROM_EMAIL}',
    file=sys.stderr,
)

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

import os
from pathlib import Path
import dj_database_url # For the PostgreSQL database
from dotenv import load_dotenv # To keep secrets safe

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
# Use an environment variable for the secret key on Render
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-key-change-this')

# Debug should be False in production
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Add your Render URL to allowed hosts
ALLOWED_HOSTS = ['.render.com', 'localhost', '127.0.0.1']


# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # For static file handling
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Essential for Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'soso_project.urls'

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
                'core.context_processors.soso_global_data', # Your custom processor
            ],
        },
    },
]

WSGI_APPLICATION = 'soso_project.wsgi.application'


# --- DATABASE ---
# On Render, use DATABASE_URL. Locally, use SQLite.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}


# --- AUTHENTICATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Redirect logic for Kifule and other traders
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL = 'login'


# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- STATIC & MEDIA FILES ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Extra places for collectstatic to find files
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# WhiteNoise compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (Images of goods/services)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# --- PRODUCTION SECURITY ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
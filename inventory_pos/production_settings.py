"""
Production settings for Render deployment
"""
import os
import dj_database_url
from decouple import config
from .settings import *

# Override settings for production
DEBUG = config('DEBUG', default=False, cast=bool)

# Security settings
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',  # Allow all Render subdomains
]

# Database - Temporarily use SQLite until PostgreSQL is working
# TODO: Switch back to PostgreSQL once psycopg2 issue is resolved
database_url = config('DATABASE_URL', default=None)
if False:  # Temporarily disabled - database_url and 'postgresql' in database_url:
    try:
        DATABASES = {
            'default': dj_database_url.parse(database_url)
        }
        DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
        DATABASES['default']['OPTIONS'] = {
            'charset': 'utf8',
        }
    except Exception as e:
        print(f"PostgreSQL configuration error: {e}")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    # Use SQLite for now (works reliably on Render)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("Using SQLite database for production (temporary)")

# Static files settings for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Static files compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files - for production, you'd want to use cloud storage
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECRET_KEY = config('SECRET_KEY', default=SECRET_KEY)

# HTTPS settings (when using custom domain)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inventory': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'pos': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
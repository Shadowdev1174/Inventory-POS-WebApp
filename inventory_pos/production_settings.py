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

# Database
try:
    # Try to parse DATABASE_URL for PostgreSQL
    database_url = config('DATABASE_URL', default=None)
    if database_url:
        DATABASES = {
            'default': dj_database_url.parse(database_url)
        }
        # Ensure correct engine for PostgreSQL
        if 'postgresql' in database_url or 'postgres' in database_url:
            DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
            # Set connection options for better compatibility
            DATABASES['default']['OPTIONS'] = {
                'charset': 'utf8',
            }
    else:
        # Fallback to SQLite for local development
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
except Exception as e:
    print(f"Database configuration error: {e}")
    # Emergency fallback to SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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
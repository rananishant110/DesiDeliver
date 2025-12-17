"""
Django settings for desideliver_backend project - Development Configuration.

This module contains development-specific settings.
Inherits from base.py and overrides settings for local development.
"""

from .base import *

# Development mode
DEBUG = True

# Database - PostgreSQL for Docker, SQLite as fallback
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': env('DB_NAME', default='desideliver_dev'),
        'USER': env('DB_USER', default='desideliver_user'),
        'PASSWORD': env('DB_PASSWORD', default='dev_password'),
        'HOST': env('DB_HOST', default='db'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# Email Configuration - Console backend for development
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = 'noreply@desideliver.com'

# Cache Configuration - Dummy cache for development (can use Redis if needed)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Logging Configuration - Verbose logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
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
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Development-specific settings
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Allow all origins in development (for testing)
# Note: This is overridden by CORS_ALLOWED_ORIGINS from .env
# But we ensure localhost is always allowed
if 'http://localhost:3000' not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append('http://localhost:3000')
if 'http://localhost:3001' not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append('http://localhost:3001')

print("🚀 Running in DEVELOPMENT mode with local.py settings")

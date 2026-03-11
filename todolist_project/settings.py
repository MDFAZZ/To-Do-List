"""
Django settings for todolist_project.

This module contains all the configuration settings for the To-Do List application.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dev-key-change-in-production-12345'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']


# Application definition

# Base installed apps
# Note: django.contrib.auth is included for Swagger compatibility
INSTALLED_APPS = [
    'django.contrib.auth',  # Required for Swagger and some Django features
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',  # DRF for @api_view decorator (not a viewset, just a decorator)
    'tasks',  # Our tasks application
]

# Try to add Swagger if available (optional)
try:
    import drf_yasg
    INSTALLED_APPS.append('drf_yasg')  # Swagger/OpenAPI documentation
except (ImportError, ModuleNotFoundError):
    # Swagger not available (e.g., Python 3.13 compatibility issue or missing pkg_resources)
    # Application will work without Swagger documentation
    pass

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'todolist_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'todolist_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'todolist.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'tasks': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Cache Configuration (using in-memory cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Swagger/OpenAPI settings for drf-yasg
# Configure to work with function-based views and disable authentication
try:
    import drf_yasg
    SWAGGER_SETTINGS = {
        'USE_SESSION_AUTH': False,  # Disable session authentication
        'LOGIN_URL': None,  # No login required
        'LOGOUT_URL': None,
        'VALIDATOR_URL': None,  # Disable schema validation
        'SECURITY_DEFINITIONS': {},  # No security definitions needed
        'DEFAULT_INFO': None,  # Will use the one from get_schema_view
    }
except ImportError:
    pass

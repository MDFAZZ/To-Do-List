# Django settings for the todo list project

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# Development settings - change these for production!

SECRET_KEY = 'django-insecure-dev-key-change-in-production-12345'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']


# Installed apps

INSTALLED_APPS = [
    'django.contrib.auth',  # Needed for Swagger
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',  # Using @api_view decorator (not viewsets)
    'tasks',  # Our main app
]

# Try to add Swagger if it's installed (optional)
try:
    import drf_yasg
    INSTALLED_APPS.append('drf_yasg')
except (ImportError, ModuleNotFoundError):
    # Swagger might not work on Python 3.13 or if pkg_resources is missing
    # App works fine without it
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


# Database - using SQLite for simplicity
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Internationalization settings

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JS, images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging setup - writes to both console and file
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

# In-memory cache (not really using it much, but Django expects it)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Swagger settings - disable auth since we don't need it
try:
    import drf_yasg
    SWAGGER_SETTINGS = {
        'USE_SESSION_AUTH': False,
        'LOGIN_URL': None,
        'LOGOUT_URL': None,
        'VALIDATOR_URL': None,
        'SECURITY_DEFINITIONS': {},
        'DEFAULT_INFO': None,
    }
except ImportError:
    pass

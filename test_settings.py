"""
Test settings for running tests without Swagger dependencies.
This allows tests to run even if drf-yasg has compatibility issues.
"""

from todolist_project.settings import *

# Remove drf_yasg from INSTALLED_APPS for testing
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'drf_yasg']

# Use in-memory cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Disable logging during tests for cleaner output
LOGGING['handlers']['console']['level'] = 'ERROR'
LOGGING['handlers']['file']['level'] = 'ERROR'

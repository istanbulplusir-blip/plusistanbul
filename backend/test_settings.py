"""
Test settings for User system testing
"""

from peykan.settings import *

# Override settings for testing
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1', 'peykantravelistanbul.com', 'www.peykantravelistanbul.com']

# Use in-memory database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Enable migrations for testing
MIGRATION_MODULES = {}

# Disable cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable logging for testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Disable email sending for testing
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Disable Celery for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

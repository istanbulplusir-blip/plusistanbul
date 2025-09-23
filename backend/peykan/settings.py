"""
Django settings for Peykan Tourism Ecommerce Platform.
"""

import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url
from dotenv import load_dotenv
import logging.config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='peykantravelistanbul.com,www.peykantravelistanbul.com,localhost,127.0.0.1,testserver', cast=Csv())

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'modeltranslation',
    'parler',
    'drf_spectacular',
    'django_celery_beat',
    # 'allauth',
    # 'allauth.account',
    # 'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google',
    # 'dj_rest_auth',
    # 'dj_rest_auth.registration',
]

if DEBUG:
    THIRD_PARTY_APPS.append('debug_toolbar')

LOCAL_APPS = [
    'peykan',
    'core.apps.CoreConfig',
    'shared.apps.SharedConfig',
    'users.apps.UsersConfig',
    'tours.apps.ToursConfig',
    'events.apps.EventsConfig',
    'transfers.apps.TransfersConfig',
    'car_rentals.apps.CarRentalsConfig',
    'cart.apps.CartConfig',
    'orders.apps.OrdersConfig',
    'payments.apps.PaymentsConfig',
    'agents.apps.AgentsConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # 'django.middleware.security.SecurityMiddleware',  # Temporarily disabled
    # 'whitenoise.middleware.WhiteNoiseMiddleware',  # Temporarily disabled
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'peykan.middleware.LanguageMiddleware',  # Custom language middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Re-enabled for production
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Temporarily disabled
    # Custom user security middleware
    'users.middleware.UserActivityMiddleware',
    'users.middleware.SecurityMiddleware',
    'users.middleware.SessionSecurityMiddleware',
]

if DEBUG:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'peykan.urls'

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

WSGI_APPLICATION = 'peykan.wsgi.application'

# SQLite WAL Mode Configuration
if DEBUG:
    from django.db.backends.signals import connection_created
    from django.dispatch import receiver
    
    @receiver(connection_created)
    def enable_sqlite_wal_mode(sender, connection, **kwargs):
        if connection.vendor == 'sqlite':
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA synchronous=NORMAL;")
                cursor.execute("PRAGMA cache_size=10000;")
                cursor.execute("PRAGMA temp_store=MEMORY;")

# Database
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 30,  # 30 seconds timeout for database operations
            }
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL', default='sqlite:///db.sqlite3')
        )
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

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_CLIENT_SECRET'),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Internationalization
LANGUAGE_CODE = config('DEFAULT_LANGUAGE', default='fa')

LANGUAGES = [
    ('fa', 'فارسی'),
    ('en', 'English'),
    ('tr', 'Türkçe'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / config('STATIC_ROOT', default='staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# Image processing settings
IMAGE_MAX_SIZE = (1920, 1080)  # Maximum image dimensions
IMAGE_QUALITY = 85  # JPEG quality for optimization
IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp']  # Allowed formats
MAX_IMAGE_SIZE_MB = 10  # Maximum file size in MB

# Media storage settings
if not DEBUG:
    # Production: Use cloud storage (AWS S3, MinIO, etc.)
    DEFAULT_FILE_STORAGE = config('DEFAULT_FILE_STORAGE', default='django.core.files.storage.FileSystemStorage')
    
    # AWS S3 Configuration (uncomment when ready)
    # AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
    # AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
    # AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
    # AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='')
    # AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')
    # AWS_S3_OBJECT_PARAMETERS = {
    #     'CacheControl': 'max-age=86400',
    # }
    # AWS_DEFAULT_ACL = 'public-read'
    # AWS_QUERYSTRING_AUTH = False
    # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    # Development: Use local file system
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Site ID
SITE_ID = 1

# Google OAuth (ID token audience)
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')

# CORS Settings
# IMPORTANT: When using credentials (cookies) the wildcard origin (*) is invalid.
# Restrict to explicit origins to avoid browser blocking and Axios ECONNABORTED.
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://peykantravelistanbul.com,https://www.peykantravelistanbul.com,http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-forwarded-for',
    'x-forwarded-proto',
]
CORS_EXPOSE_HEADERS = [
    'content-type',
    'content-length',
    'x-total-count',
    'cache-control',
    'access-control-allow-origin',
]

# CORS Media settings
CORS_ALLOW_MEDIA = True
CORS_MEDIA_HEADERS = [
    'content-type',
    'content-length',
    'cache-control',
    'last-modified',
    'etag',
]

# CSRF trusted origins for cross-site requests from the frontend dev server
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)

# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend',
#     'allauth.account.auth_backends.AuthenticationBackend',
# ]

# URL Settings
APPEND_SLASH = False  # Disable for API endpoints
PREPEND_WWW = False

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ),
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=120, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=config('JWT_REFRESH_TOKEN_LIFETIME', default=1440, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Redis Cache Settings
# Use local memory cache in development to avoid DB cache table requirement
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'local-cache',
    }
}

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-reservations': {
        'task': 'events.tasks.cleanup_expired_reservations',
        'schedule': 300.0,  # Every 5 minutes
    },
    'cleanup-expired-carts': {
        'task': 'cart.tasks.cleanup_expired_carts',
        'schedule': 600.0,  # Every 10 minutes
    },
    'update-capacity-cache': {
        'task': 'events.tasks.update_capacity_cache',
        'schedule': 1800.0,  # Every 30 minutes
    },
}

# Session Settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = True

# Email Settings
if DEBUG:
    # Development: Use console backend (print emails to console)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production: Use SMTP backend
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@peykan.com')
SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='support@peykan.com')

# WhatsApp configuration
WHATSAPP_SUPPORT_NUMBER = config('WHATSAPP_SUPPORT_NUMBER', default='989123456789')
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# Currency Settings
DEFAULT_CURRENCY = config('DEFAULT_CURRENCY', default='USD')
SUPPORTED_CURRENCIES = config('SUPPORTED_CURRENCIES', default='USD,EUR,TRY,IRR').split(',')

# Kavenegar SMS Settings
KAVENEGAR_API_KEY = config('KAVENEGAR_API_KEY', default='')

# Payment Gateway Settings
PAYMENT_GATEWAY = config('PAYMENT_GATEWAY', default='mock')
PAYMENT_SECRET_KEY = config('PAYMENT_SECRET_KEY', default='')

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Peykan Tourism API',
    'DESCRIPTION': 'Multilingual, multi-currency booking platform API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
}

# Debug Toolbar (Development only)
if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]

# Model Translation Settings
MODELTRANSLATION_DEFAULT_LANGUAGE = 'fa'
MODELTRANSLATION_LANGUAGES = ('fa', 'en', 'tr')

# Parler Settings
PARLER_LANGUAGES = {
    SITE_ID: (
        {'code': 'fa', 'name': 'فارسی', 'fallback': True},
        {'code': 'en', 'name': 'English'},
        {'code': 'tr', 'name': 'Türkçe'},
    ),
    'default': {
        'fallback': 'fa',
        'hide_untranslated': False,
        'redirect_on_fallback': False,
    }
}

# Parler specific settings
PARLER_DEFAULT_LANGUAGE_CODE = 'fa'
PARLER_SHOW_EXCLUDED_LANGUAGE_TABS = True
PARLER_ENABLE_CACHING = False

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = config('FILE_UPLOAD_MAX_MEMORY_SIZE', default=10, cast=int) * 1024 * 1024  # Configurable MB
DATA_UPLOAD_MAX_MEMORY_SIZE = config('DATA_UPLOAD_MAX_MEMORY_SIZE', default=10, cast=int) * 1024 * 1024  # Configurable MB

# File upload handlers
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# Media file permissions
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Image processing
PIL_JPEG_QUALITY = IMAGE_QUALITY
PIL_JPEG_OPTIMIZE = True

# Security Settings (Production)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None
    CSRF_COOKIE_SECURE = True

# Logging Configuration
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
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
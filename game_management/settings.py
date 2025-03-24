import os
import sys
from datetime import timedelta
from pathlib import Path

from core.settings import Settings

BASE_DIR = Path(__file__).resolve().parent.parent

settings = Settings()

SECRET_KEY = settings.DJANGO_SECRET_KEY
DEBUG = settings.DJANGO_DEBUG
ALLOWED_HOSTS = settings.DJANGO_ALLOWED_HOSTS.split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_celery_beat",
    "games",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}

ROOT_URLCONF = "game_management.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "game_management.asgi.application"

if "pytest" in sys.modules:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": settings.DJANGO_DB_NAME,
            "USER": settings.DJANGO_DB_USER,
            "PASSWORD": settings.DJANGO_DB_PASSWORD,
            "HOST": settings.DJANGO_DB_HOST,
            "PORT": settings.DJANGO_DB_PORT,
        }
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "loguru": {
            "level": settings.DJANGO_LOG_LEVEL,
            "class": "core.logger.InterceptHandler",
        },
    },
    "root": {
        "handlers": ["loguru"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["loguru"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["loguru"],
            "level": "ERROR",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["loguru"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

if not settings.COLLECT_STATIC:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static"),
    ]
else:
    STATICFILES_DIRS = []

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

LANGUAGE_CODE = "en-us"
TIME_ZONE = settings.TZ
USE_I18N = True
USE_L10N = True
USE_TZ = True

CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = settings.TZ

CELERY_BEAT_SCHEDULE = {
    "generate_monthly_reports": {
        "task": "games.tasks.generate_monthly_reports",
        "schedule": timedelta(days=1),
    },
    "generate_session_ratio": {
        "task": "games.tasks.generate_session_ratio",
        "schedule": timedelta(days=1),
    },
}

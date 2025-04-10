import os
from datetime import timedelta
from pathlib import Path

from core.settings import Settings

BASE_DIR = Path(__file__).resolve().parent.parent

Settings = Settings()

SECRET_KEY = Settings.DJANGO_SECRET_KEY
DEBUG = Settings.DJANGO_DEBUG
ALLOWED_HOSTS = Settings.DJANGO_ALLOWED_HOSTS.split(",")

INSTALLED_APPS = [
    "jet",
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
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
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

if os.getenv("ENV", "dev") == "dev":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "local.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": Settings.DJANGO_DB_NAME,
            "USER": Settings.DJANGO_DB_USER,
            "PASSWORD": Settings.DJANGO_DB_PASSWORD,
            "HOST": Settings.DJANGO_DB_HOST,
            "PORT": Settings.DJANGO_DB_PORT,
        }
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "loguru": {
            "level": Settings.DJANGO_LOG_LEVEL,
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

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

CSRF_TRUSTED_ORIGINS = [Settings.CSRF_TRUSTED_ORIGINS]

LANGUAGE_CODE = "en-us"
TIME_ZONE = Settings.TZ
USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = Settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = Settings.CELERY_RESULT_BACKEND
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = Settings.TZ

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

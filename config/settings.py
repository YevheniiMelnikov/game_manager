import os
from pathlib import Path

from config.logger import *
from config.celery import *


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = Settings.DJANGO_SECRET_KEY
DEBUG = Settings.DJANGO_DEBUG
ALLOWED_HOSTS = Settings.DJANGO_ALLOWED_HOSTS.split(",")
AUTH_USER_MODEL = "users.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DJANGO_SUPERUSER_USERNAME = Settings.DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_PASSWORD = Settings.DJANGO_SUPERUSER_PASSWORD

INSTALLED_APPS = [
    "jet",
    "apps.games.apps.GamesConfig",
    "apps.users.apps.UsersConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "django_celery_beat",
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
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "GameManager API",
    "DESCRIPTION": "GameManager app API documentation",
    "VERSION": "1.0.0",
}

ROOT_URLCONF = "config.urls"

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

ASGI_APPLICATION = "config.asgi.application"

if Settings.ENV == "dev":
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

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

CSRF_TRUSTED_ORIGINS = [Settings.CSRF_TRUSTED_ORIGINS]

LANGUAGE_CODE = "en-us"
TIME_ZONE = Settings.TZ
USE_I18N = True
USE_L10N = True
USE_TZ = True

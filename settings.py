import os
from dataclasses import dataclass


@dataclass
class Settings:
    DJANGO_SECRET_KEY: str = os.getenv("DJANGO_SECRET_KEY")
    DJANGO_DEBUG: bool = os.getenv("DJANGO_DEBUG", "False") == "True"
    DJANGO_ALLOWED_HOSTS: str = os.getenv("DJANGO_ALLOWED_HOSTS", "*")
    DJANGO_LOG_LEVEL: str = os.getenv("DJANGO_LOG_LEVEL", "INFO")
    DJANGO_HOST: str = os.getenv("DJANGO_HOST")
    DJANGO_PORT: int = int(os.getenv("DJANGO_PORT"))
    API_URL: str = os.getenv("API_URL")
    DOMAIN: str = os.getenv("DOMAIN")

    DJANGO_DB_NAME: str = os.getenv("DJANGO_DB_NAME")
    DJANGO_DB_USER: str = os.getenv("DJANGO_DB_USER")
    DJANGO_DB_PASSWORD: str = os.getenv("DJANGO_DB_PASSWORD")
    DJANGO_DB_HOST: str = os.getenv("DJANGO_DB_HOST")
    DJANGO_DB_PORT: int = int(os.getenv("DJANGO_DB_PORT"))

    DJANGO_SUPERUSER_USERNAME: str = os.getenv("DJANGO_SUPERUSER_USERNAME")
    DJANGO_SUPERUSER_PASSWORD: str = os.getenv("DJANGO_SUPERUSER_PASSWORD")

    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT"))

    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")

    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    REDIS_URL: str = os.getenv("REDIS_URL")

    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND")

    TZ: str = os.getenv("TZ")
    CSRF_TRUSTED_ORIGINS: str = os.getenv("CSRF_TRUSTED_ORIGINS")

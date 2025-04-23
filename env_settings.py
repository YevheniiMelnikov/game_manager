import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def must_getenv(key: str, default: Optional[str] = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


@dataclass
class Settings:
    DJANGO_SECRET_KEY: str = must_getenv("DJANGO_SECRET_KEY")
    DJANGO_DEBUG: bool = os.getenv("DJANGO_DEBUG", "False") == "True"
    DJANGO_ALLOWED_HOSTS: str = os.getenv("DJANGO_ALLOWED_HOSTS", "*")
    DJANGO_LOG_LEVEL: str = os.getenv("DJANGO_LOG_LEVEL", "INFO")
    DJANGO_HOST: str = must_getenv("DJANGO_HOST")
    DJANGO_PORT: int = int(must_getenv("DJANGO_PORT"))
    API_URL: str = must_getenv("API_URL")
    DOMAIN: str = must_getenv("DOMAIN")

    DJANGO_DB_NAME: str = must_getenv("DJANGO_DB_NAME")
    DJANGO_DB_USER: str = must_getenv("DJANGO_DB_USER")
    DJANGO_DB_PASSWORD: str = must_getenv("DJANGO_DB_PASSWORD")
    DJANGO_DB_HOST: str = must_getenv("DJANGO_DB_HOST")
    DJANGO_DB_PORT: int = int(must_getenv("DJANGO_DB_PORT"))

    DJANGO_SUPERUSER_USERNAME: str = must_getenv("DJANGO_SUPERUSER_USERNAME")
    DJANGO_SUPERUSER_PASSWORD: str = must_getenv("DJANGO_SUPERUSER_PASSWORD")

    DB_NAME: str = must_getenv("DB_NAME")
    DB_USER: str = must_getenv("DB_USER")
    DB_PASSWORD: str = must_getenv("DB_PASSWORD")
    DB_HOST: str = must_getenv("DB_HOST")
    DB_PORT: int = int(must_getenv("DB_PORT"))

    POSTGRES_USER: str = must_getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = must_getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = must_getenv("POSTGRES_DB")

    REDIS_HOST: str = must_getenv("REDIS_HOST")
    REDIS_PORT: int = int(must_getenv("REDIS_PORT"))
    REDIS_URL: str = must_getenv("REDIS_URL")

    CELERY_BROKER_URL: str = must_getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = must_getenv("CELERY_RESULT_BACKEND")

    TZ: str = must_getenv("TZ")
    CSRF_TRUSTED_ORIGINS: str = must_getenv("CSRF_TRUSTED_ORIGINS")

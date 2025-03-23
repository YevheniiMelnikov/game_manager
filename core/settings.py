import os
from dataclasses import dataclass


@dataclass
class Settings:
    DJANGO_SECRET_KEY: str = os.getenv("DJANGO_SECRET_KEY")
    DJANGO_DEBUG: bool = os.getenv("DJANGO_DEBUG", "False") == "True"
    DJANGO_ALLOWED_HOSTS: str = os.getenv("DJANGO_ALLOWED_HOSTS", "*")
    DJANGO_LOG_LEVEL: str = os.getenv("DJANGO_LOG_LEVEL", "INFO")
    DJANGO_HOST: str = os.getenv("DJANGO_HOST", "api")
    DJANGO_PORT: int = int(os.getenv("DJANGO_PORT", 8000))
    API_URL: str = os.getenv("API_URL", "http://localhost:8000/")
    DOMAIN: str = os.getenv("DOMAIN", "localhost")

    DJANGO_DB_NAME: str = os.getenv("DJANGO_DB_NAME", "game_management")
    DJANGO_DB_USER: str = os.getenv("DJANGO_DB_USER", "postgres")
    DJANGO_DB_PASSWORD: str = os.getenv("DJANGO_DB_PASSWORD", "postgres")
    DJANGO_DB_HOST: str = os.getenv("DJANGO_DB_HOST", "db")
    DJANGO_DB_PORT: int = int(os.getenv("DJANGO_DB_PORT", 5432))

    COLLECT_STATIC: bool = os.getenv("COLLECT_STATIC", "False") == "True"

    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

    TZ: str = os.getenv("TZ", "Europe/Kyiv")

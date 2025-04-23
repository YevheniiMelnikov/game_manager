from django.apps import AppConfig

from env_settings import Settings
from loguru import logger


class GamesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "games"

    def ready(self):
        from django.contrib.auth import get_user_model
        from django.db.utils import OperationalError

        User = get_user_model()

        try:
            username = Settings.DJANGO_SUPERUSER_USERNAME
            password = Settings.DJANGO_SUPERUSER_PASSWORD

            if username and password and not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, password=password)
        except OperationalError:
            logger.error("Database not ready")

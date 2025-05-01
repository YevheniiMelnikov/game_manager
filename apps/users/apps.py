from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from loguru import logger


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    def ready(self):
        post_migrate.connect(create_superuser, sender=self)


def create_superuser(sender, **kwargs) -> None:
    User = get_user_model()
    username = settings.DJANGO_SUPERUSER_USERNAME
    password = settings.DJANGO_SUPERUSER_PASSWORD

    if not username or not password:
        logger.warning("Superuser credentials not provided")
        return

    user, created = User.objects.get_or_create(username=username)
    if created:
        user.is_superuser = True
        user.is_staff = True
        user.set_password(password)
        user.save()
        logger.success(f"Superuser '{username}' created")
    else:
        logger.info(f"Superuser '{username}' already exists")

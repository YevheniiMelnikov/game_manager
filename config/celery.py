from celery import Celery
from celery.schedules import crontab

from config.env_settings import Settings

app = Celery("game_management")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

CELERY_BROKER_URL = Settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = Settings.CELERY_RESULT_BACKEND
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = Settings.TZ
CELERY_BEAT_SCHEDULE = {
    "generate_monthly_reports": {
        "task": "games.tasks.generate_monthly_reports",
        "schedule": crontab(minute=0, hour=0, day_of_month=1),
    },
    "generate_session_ratio": {
        "task": "games.tasks.generate_session_ratio",
        "schedule": crontab(minute=0, hour=0, day_of_month=1),
    },
}

from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.games.models import Company
from apps.games.schemas import SessionMetrics
from apps.users.enums import UserRole


class User(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices(),
        default=UserRole.PARTICIPANT.value,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_sessions_metrics(self) -> SessionMetrics:
        sessions_qs = self.game_sessions.all()
        total = sessions_qs.count()
        completed = sessions_qs.filter(results__is_completed=True).distinct().count()
        failed = total - completed

        return SessionMetrics(
            completed=completed,
            failed=failed,
            total=total,
            completion_ratio=round(completed / total, 2) if total else 0,
            failure_ratio=round(failed / total, 2) if total else 0,
        )

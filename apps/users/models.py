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

    @property
    def total_sessions(self) -> int:
        return self.game_sessions.count()

    @property
    def completed_sessions(self) -> int:
        return self.game_sessions.filter(results__is_completed=True).distinct().count()

    @property
    def failed_sessions(self) -> int:
        return self.game_sessions.exclude(results__is_completed=True).distinct().count()

    @property
    def completion_ratio(self) -> float:
        total = self.total_sessions
        return round(self.completed_sessions / total, 2) if total else 0

    @property
    def failure_ratio(self) -> float:
        total = self.total_sessions
        return round(self.failed_sessions / total, 2) if total else 0

    def get_sessions_metrics(self) -> SessionMetrics:
        total = self.total_sessions
        return SessionMetrics(
            completed=self.completed_sessions,
            failed=self.failed_sessions,
            total=total,
            completion_ratio=self.completion_ratio,
            failure_ratio=self.failure_ratio,
        )

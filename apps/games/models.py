from django.db import models

from apps.games.enums import GameCategory, GameSessionStatus
from apps.games.schemas import SessionMetrics
from config.settings import AUTH_USER_MODEL


class Game(models.Model):
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    category = models.CharField(
        max_length=20,
        choices=GameCategory.choices(),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    @property
    def completed_sessions(self) -> int:
        return self.sessions.filter(results__is_completed=True).distinct().count()

    @property
    def total_sessions(self) -> int:
        return self.sessions.count()

    @property
    def failed_sessions(self) -> int:
        return self.sessions.exclude(results__is_completed=True).distinct().count()

    @property
    def completion_ratio(self) -> float:
        total = self.total_sessions
        return round(self.completed_sessions / total, 2) if total else 0

    @property
    def failure_ratio(self) -> float:
        total = self.total_sessions
        return round(self.failed_sessions / total, 2) if total else 0

    def get_session_metrics(self) -> SessionMetrics:
        total = self.total_sessions
        return SessionMetrics(
            completed=self.completed_sessions,
            failed=self.failed_sessions,
            total=total,
            completion_ratio=round(self.completed_sessions / total, 2) if total else 0,
            failure_ratio=round(self.failed_sessions / total, 2) if total else 0,
        )

    class Meta:
        verbose_name = "Game"
        verbose_name_plural = "Games"


class GameSession(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="sessions")
    start_datetime = models.DateTimeField(db_index=True)
    participants = models.ManyToManyField(AUTH_USER_MODEL, related_name="game_sessions")
    status = models.CharField(
        max_length=20,
        choices=GameSessionStatus.choices(),
        default=GameSessionStatus.CREATED.value,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_datetime"]
        verbose_name = "Game Session"
        verbose_name_plural = "Game Sessions"

    def __str__(self) -> str:
        return f"Session of {self.game.name} at {self.start_datetime}"


class GameResults(models.Model):
    game_session = models.OneToOneField(GameSession, on_delete=models.CASCADE, related_name="results")
    score = models.IntegerField()
    is_completed = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Result for session {self.game_session.id} - Score: {self.score}"

    class Meta:
        verbose_name = "Game Result"
        verbose_name_plural = "Game Results"


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Company: {self.name}"

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

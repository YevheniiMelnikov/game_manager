from django.db import models
from django.contrib.auth.models import AbstractUser


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("SuperAdmin", "SuperAdmin"),
        ("CompanyAdmin", "CompanyAdmin"),
        ("Participant", "Participant"),
    ]
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Participant")

    def get_sessions_metrics(self) -> dict:
        sessions_qs = self.game_sessions.all()
        total_sessions = sessions_qs.count()
        completed_sessions = sessions_qs.filter(results__is_completed=True).distinct().count()
        failed_sessions = total_sessions - completed_sessions
        return {
            "completed": completed_sessions,
            "failed": failed_sessions,
            "total": total_sessions,
            "completion_ratio": round(completed_sessions / total_sessions, 2) if total_sessions else 0,
            "failure_ratio": round(failed_sessions / total_sessions, 2) if total_sessions else 0,
        }


class Game(models.Model):
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    category = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

    @property
    def completed_sessions(self) -> int:
        return self.sessions.filter(results__is_completed=True).distinct().count()

    def get_session_metrics(self) -> dict:
        sessions_qs = self.sessions.all()
        total_sessions = sessions_qs.count()
        failed_sessions = total_sessions - self.completed_sessions
        return {
            "completed": self.completed_sessions,
            "failed": failed_sessions,
            "total": total_sessions,
            "completion_ratio": round(self.completed_sessions / total_sessions, 2) if total_sessions else 0,
            "failure_ratio": round(failed_sessions / total_sessions, 2) if total_sessions else 0,
        }

    class Meta:
        verbose_name = "Game"
        verbose_name_plural = "Games"


class GameSession(models.Model):
    STATUS_CHOICES = [
        ("Created", "Created"),
        ("InProgress", "In Progress"),
        ("Finished", "Finished"),
        ("Filed", "Filed"),
    ]
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="sessions")
    start_datetime = models.DateTimeField(db_index=True)
    participants = models.ManyToManyField("games.CustomUser", related_name="game_sessions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Created")

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

    def __str__(self) -> str:
        return f"Result for session {self.game_session.id} - Score: {self.score}"

    class Meta:
        verbose_name = "Game Result"
        verbose_name_plural = "Game Results"

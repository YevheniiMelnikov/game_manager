from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Participant(models.Model):
    ROLES = [
        ("SuperAdmin", "SuperAdmin"),
        ("CompanyAdmin", "CompanyAdmin"),
        ("Participant", "Participant"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="participant_profile")
    role = models.CharField(max_length=20, choices=ROLES)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Game(models.Model):
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class GameSession(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="sessions")
    start_datetime = models.DateTimeField()
    participants = models.ManyToManyField(User, related_name="game_sessions")

    def __str__(self):
        return f"Session of {self.game.name} at {self.start_datetime}"


class GameResults(models.Model):
    STATUS_CHOICES = [
        ("Created", "Created"),
        ("InProgress", "In Progress"),
        ("Finished", "Finished"),
        ("Filed", "Filed"),
    ]
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="results")
    score = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    is_completed = models.BooleanField()

    def __str__(self):
        return f"Result for session {self.game_session.id} - {self.status} - Score: {self.score}"

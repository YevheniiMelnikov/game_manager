from django.db import models
from django.contrib.auth.models import User


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
        ("Failed", "Failed"),
    ]

    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="results")
    score = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    is_completed = models.BooleanField()

    def __str__(self):
        return f"Result for session {self.game_session.id} - {self.status} - Score: {self.score}"

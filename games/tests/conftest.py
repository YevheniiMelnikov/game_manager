import pytest
from games.models import Game, GameSession, GameResults, Participant
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from datetime import datetime


@pytest.fixture
def game():
    return Game.objects.create(name="Test Game", language="EN", category="Action")


@pytest.fixture
def user():
    return User.objects.create(username="test_user")


@pytest.fixture
def participant(user):
    return Participant.objects.create(user=user, role="Participant")


@pytest.fixture
def game_session(game, user):
    session = GameSession.objects.create(
        game=game,
        start_datetime=make_aware(datetime(2025, 3, 23, 14, 0, 0)),
    )
    session.participants.add(user)
    return session


@pytest.fixture
def game_result(game_session):
    return GameResults.objects.create(
        game_session=game_session,
        score=100,
        status="Finished",
        is_completed=True,
    )

import os
import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_management.settings")
django.setup()


@pytest.fixture
def user(db):
    from django.contrib.auth.models import User

    return User.objects.create_user(username="testuser", password="pass")


@pytest.fixture
def participant(user):
    from games.models import Participant

    return Participant.objects.create(user=user, role="Participant")


@pytest.fixture
def game():
    from games.models import Game

    return Game.objects.create(name="Memory Game", language="EN", category="Cognitive")


@pytest.fixture
def game_session(game, user):
    from games.models import GameSession
    from django.utils.timezone import make_aware
    from datetime import datetime

    session = GameSession.objects.create(
        game=game,
        start_datetime=make_aware(datetime(2025, 3, 23, 14, 0, 0)),
    )
    session.participants.add(user)
    return session


@pytest.fixture
def game_result(game_session):
    from games.models import GameResults

    return GameResults.objects.create(
        game_session=game_session,
        score=100,
        status="Finished",
        is_completed=True,
    )

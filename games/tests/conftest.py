import os
import django
import pytest
from dotenv import load_dotenv
from django.contrib.auth import get_user_model
from games.models import Game, GameSession, GameResults, CustomUser
from django.utils.timezone import make_aware
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_management.settings")
load_dotenv()
django.setup()


@pytest.fixture
def user(db) -> CustomUser:
    User = get_user_model()
    return User.objects.create_user(username="testuser", password="pass")


@pytest.fixture
def game(db) -> Game:
    return Game.objects.create(name="Memory Game", language="EN", category="Cognitive")


@pytest.fixture
def game_session(db, game: Game, user: CustomUser) -> GameSession:
    session = GameSession.objects.create(
        game=game,
        start_datetime=make_aware(datetime.now()),
    )
    session.participants.add(user)
    return session


@pytest.fixture
def game_result(db, game_session: GameSession) -> GameResults:
    return GameResults.objects.create(
        game_session=game_session,
        score=100,
        is_completed=True,
    )

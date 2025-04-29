import pytest

from pytest_factoryboy import register

from apps.games.tests.factories import GameFactory, GameSessionFactory, GameResultsFactory
from apps.users.tests.factories import UserFactory

register(UserFactory)
register(GameFactory)
register(GameSessionFactory)
register(GameResultsFactory)


@pytest.fixture(autouse=True)
def freeze_time(freezer):
    freezer.move_to("2025-02-01T00:00:00Z")


@pytest.fixture(autouse=True)
def patch_reports_dir(tmp_path, monkeypatch):
    from apps.games import utils

    monkeypatch.setattr(utils, "REPORTS_DIR", str(tmp_path))

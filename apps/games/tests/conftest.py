from unittest.mock import patch

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
def patch_reports_dir(tmp_path):
    from apps.games import utils

    utils.REPORTS_DIR = tmp_path

    with patch("apps.games.tasks.save_report") as mocked:
        def side_effect(filename, data):
            path = tmp_path / filename
            path.write_text(
                utils.json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True, default=str),
                encoding="utf-8"
            )
        mocked.side_effect = side_effect
        yield

import json
from datetime import datetime
from pathlib import Path
import pytest
from freezegun import freeze_time
from django.utils.timezone import make_aware

from apps.games.tasks import generate_monthly_reports, generate_session_ratio
import apps.games.utils as game_utils


def read_report(filepath: Path) -> dict:
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


@pytest.mark.django_db(transaction=True)
@freeze_time("2025-02-15")
def test_generate_monthly_reports(user_factory, game_factory, game_session_factory, game_results_factory) -> None:
    user = user_factory()
    game = game_factory()
    session = game_session_factory(game=game, participants=[user])
    game_results_factory(game_session=session, score=100, is_completed=True)
    result = generate_monthly_reports()

    assert result, "Monthly report generation returned empty result."
    assert game.name in result
    assert result[game.name]["participants"]
    assert all("total_score" in p for p in result[game.name]["participants"])

    files = list(game_utils.REPORTS_DIR.glob("monthly_report_*.json"))
    assert files, f"Monthly report file not found in {game_utils.REPORTS_DIR.resolve()}"


@pytest.mark.django_db(transaction=True)
def test_generate_session_ratio(game, game_session, game_results) -> None:
    result = generate_session_ratio()
    assert result, "Session ratio report generation returned empty result."
    assert "by_game" in result
    assert "by_participant" in result
    assert "overall" in result

    overall = result["overall"]
    assert "completed" in overall and "failed" in overall and "completion_ratio" in overall

    files = list(game_utils.REPORTS_DIR.glob("session_ratio_*.json"))
    assert files, "Session ratio report file not found in REPORTS_DIR."


@pytest.mark.django_db(transaction=True)
def test_monthly_report_score_sum(user) -> None:
    from apps.games.models import Game, GameSession, GameResults

    game = Game.objects.create(name="Test Game", language="EN", category="Puzzle")
    start_time = make_aware(datetime(2025, 1, 15))

    session1 = GameSession.objects.create(game=game, start_datetime=start_time)
    session1.participants.add(user)
    GameResults.objects.create(game_session=session1, score=200, is_completed=True)

    session2 = GameSession.objects.create(game=game, start_datetime=start_time)
    session2.participants.add(user)
    GameResults.objects.create(game_session=session2, score=300, is_completed=True)

    report = generate_monthly_reports()
    participants = report[game.name]["participants"]
    total_score = sum(
        p["total_score"] for p in participants if p["game_session_participants_username"] == user.username
    )

    assert total_score == 500


@pytest.mark.django_db(transaction=True)
def test_session_ratio_logic(user) -> None:
    from apps.games.models import Game, GameSession, GameResults

    game = Game.objects.create(name="Ratio Game", language="EN", category="Logic")
    for is_completed in [True, True, False]:
        session = GameSession.objects.create(game=game, start_datetime=user.date_joined)
        session.participants.add(user)
        GameResults.objects.create(game_session=session, score=100, is_completed=is_completed)

    report = generate_session_ratio()
    game_report = report["by_game"][game.name]

    assert game_report["completed"] == 2
    assert game_report["failed"] == 1

    expected_completion_ratio = round(2 / 3, 2)
    expected_failure_ratio = round(1 / 3, 2)

    assert game_report["completion_ratio"] == expected_completion_ratio
    assert game_report["failure_ratio"] == expected_failure_ratio

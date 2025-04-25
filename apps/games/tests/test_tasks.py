import os
import json
from pathlib import Path
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from apps.games.models import Game, GameSession, GameResults
from apps.games.tasks import generate_monthly_reports, generate_session_ratio
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

User = get_user_model()


def read_report(filepath: Path) -> dict[str, Any]:
    with open(filepath, "r") as file:
        return json.load(file)


@pytest.mark.django_db
def test_generate_monthly_reports(
    tmp_path: Path, game: Game, game_session: GameSession, game_result: GameResults
) -> None:
    from apps.games import tasks

    tasks.REPORTS_DIR = str(tmp_path)
    tasks.get_last_month_range = lambda: (
        make_aware(datetime.now() - timedelta(days=1)),
        make_aware(datetime.now() + timedelta(days=1)),
    )
    result = generate_monthly_reports()
    assert result is not None, "Monthly report generation failed"
    monthly_files = [f for f in os.listdir(tmp_path) if f.startswith("monthly_report_")]
    latest_report = sorted(monthly_files)[-1]
    report_data = read_report(tmp_path / latest_report)
    assert isinstance(report_data, dict), "Monthly report data should be a dictionary"
    for game_name, data in report_data.items():
        assert "participants" in data, f"Participants not found in report for game {game_name}"
        for participant in data["participants"]:
            assert "game_session__participants__username" in participant, "Username missing in report"
            assert "total_score" in participant, "Total score missing in report"


@pytest.mark.django_db
def test_generate_session_ratio(
    tmp_path: Path, game: Game, game_session: GameSession, game_result: GameResults
) -> None:
    from apps.games import tasks

    tasks.REPORTS_DIR = str(tmp_path)
    result = generate_session_ratio()
    assert result is not None, "Session ratio report generation failed"
    ratio_files = [f for f in os.listdir(tmp_path) if f.startswith("session_ratio_")]
    latest_report = sorted(ratio_files)[-1]
    report_data = read_report(tmp_path / latest_report)
    for section in ["by_game", "by_participant"]:
        assert section in report_data, f"Section {section} missing in session ratio report"
        for key, data in report_data[section].items():
            for field in ["completed", "failed", "total", "completion_ratio", "failure_ratio"]:
                assert field in data, f"{field} missing for {key} in section {section}"
    assert "overall" in report_data, "Overall section missing in session ratio report"
    overall = report_data["overall"]
    for key in ["completed", "failed", "total", "completion_ratio", "failure_ratio"]:
        assert key in overall, f"{key} missing in overall section"


@pytest.mark.django_db
def test_monthly_report_score_sum(tmp_path: Path) -> None:
    from apps.games import tasks

    tasks.REPORTS_DIR = str(tmp_path)
    tasks.get_last_month_range = lambda: (
        make_aware(datetime.now() - timedelta(days=1)),
        make_aware(datetime.now() + timedelta(days=1)),
    )
    user = User.objects.create(username="tester")
    game = Game.objects.create(name="Test Game", language="EN", category="Puzzle")
    session = GameSession.objects.create(game=game, start_datetime=make_aware(datetime.now()))
    session.participants.add(user)
    GameResults.objects.create(game_session=session, score=200, is_completed=True)
    session2 = GameSession.objects.create(game=game, start_datetime=make_aware(datetime.now()))
    session2.participants.add(user)
    GameResults.objects.create(game_session=session2, score=300, is_completed=True)
    report = generate_monthly_reports()
    participants = report[game.name]["participants"]
    total_score_for_tester = sum(
        p["total_score"] for p in participants if p["game_session__participants__username"] == "tester"
    )
    assert total_score_for_tester == 500, f"Expected total score 500 for tester, got {total_score_for_tester}"


@pytest.mark.django_db
def test_session_ratio_logic(tmp_path: Path) -> None:
    from apps.games import tasks

    tasks.REPORTS_DIR = str(tmp_path)
    user = User.objects.create(username="ratio_tester")
    game = Game.objects.create(name="Ratio Game", language="EN", category="Logic")
    for is_completed in [True, True, False]:
        session = GameSession.objects.create(game=game, start_datetime=make_aware(datetime.now()))
        session.participants.add(user)
        GameResults.objects.create(game_session=session, score=100, is_completed=is_completed)
    report = generate_session_ratio()
    by_game = report["by_game"][game.name]
    by_participant = report["by_participant"][user.username]
    assert by_game["completed"] == 2
    assert by_game["failed"] == 1
    assert by_game["completion_ratio"] == 0.67
    assert by_participant["failed"] == 1
    assert by_participant["total"] == 3
    assert report["overall"]["total"] == 3

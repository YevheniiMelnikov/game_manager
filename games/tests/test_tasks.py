import os
import pytest
import json
from games.tasks import generate_monthly_reports, generate_session_ratio

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_management.settings")

REPORTS_DIR = "/app/reports/"


def read_report(filename):
    file_path = os.path.join(REPORTS_DIR, filename)
    with open(file_path, "r") as file:
        return json.load(file)


@pytest.mark.django_db
def test_generate_monthly_reports(game, game_session, game_result):
    result = generate_monthly_reports()
    assert result is not None, "Monthly report generation failed"
    monthly_files = [f for f in os.listdir(REPORTS_DIR) if f.startswith("monthly_report_")]
    latest_report = sorted(monthly_files)[-1]
    report_data = read_report(latest_report)
    assert isinstance(report_data, dict), "Monthly report data should be a dictionary"
    for game_name, data in report_data.items():
        assert "participants" in data, f"Participants not found in report for game {game_name}"


@pytest.mark.django_db
def test_generate_session_ratio(game, game_session, game_result):
    result = generate_session_ratio()
    assert result is not None, "Session ratio report generation failed"
    ratio_files = [f for f in os.listdir(REPORTS_DIR) if f.startswith("session_ratio_")]
    latest_report = sorted(ratio_files)[-1]
    report_data = read_report(latest_report)
    assert isinstance(report_data, dict), "Session ratio data should be a dictionary"
    for game_name, data in report_data.items():
        assert "completed" in data, f"Completed count missing for game {game_name}"
        assert "failed" in data, f"Failed count missing for game {game_name}"
        assert "total" in data, f"Total count missing for game {game_name}"
        assert "completion_ratio" in data, f"Completion ratio missing for game {game_name}"
        assert "failure_ratio" in data, f"Failure ratio missing for game {game_name}"

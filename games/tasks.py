from celery import shared_task
from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils.timezone import now
from django.conf import settings
from games.models import Game, GameSession, Participant, GameResults
import logging
import os
import json

logger = logging.getLogger(__name__)

REPORTS_DIR = os.path.join(settings.BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def clear_reports(prefix):
    for filename in os.listdir(REPORTS_DIR):
        if filename.startswith(prefix):
            os.remove(os.path.join(REPORTS_DIR, filename))


def save_report(filename, data):
    file_path = os.path.join(REPORTS_DIR, filename)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    logger.info(f"Report saved to {file_path}")


@shared_task
def generate_monthly_reports():
    last_month = now() - timedelta(days=30)
    report = {}
    clear_reports("monthly_report_")
    for game in Game.objects.all():
        participants = (
            GameResults.objects.filter(game_session__game=game, game_session__start_datetime__gte=last_month)
            .values("game_session__participants__username")
            .annotate(total_score=Sum("score"))
        )
        report[game.name] = {"participants": list(participants)}
    filename = f"monthly_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    logging.info("Monthly report saved")
    return report


@shared_task
def generate_session_ratio():
    report = {}
    clear_reports("session_ratio_")

    report["by_game"] = {}
    for game in Game.objects.all():
        sessions_qs = game.sessions.all()
        total_sessions = sessions_qs.count()
        completed_sessions = sessions_qs.filter(results__is_completed=True).distinct().count()
        failed_sessions = total_sessions - completed_sessions
        report["by_game"][game.name] = {
            "completed": completed_sessions,
            "failed": failed_sessions,
            "total": total_sessions,
            "completion_ratio": round(completed_sessions / total_sessions, 2) if total_sessions else 0,
            "failure_ratio": round(failed_sessions / total_sessions, 2) if total_sessions else 0,
        }

    report["by_participant"] = {}
    for participant in Participant.objects.all():
        sessions_qs = participant.user.game_sessions.all()
        total_sessions = sessions_qs.count()
        completed_sessions = sessions_qs.filter(results__is_completed=True).distinct().count()
        failed_sessions = total_sessions - completed_sessions
        report["by_participant"][participant.user.username] = {
            "completed": completed_sessions,
            "failed": failed_sessions,
            "total": total_sessions,
            "completion_ratio": round(completed_sessions / total_sessions, 2) if total_sessions else 0,
            "failure_ratio": round(failed_sessions / total_sessions, 2) if total_sessions else 0,
        }

    all_sessions = GameSession.objects.all()
    total_sessions = all_sessions.count()
    completed_sessions = all_sessions.filter(results__is_completed=True).distinct().count()
    failed_sessions = total_sessions - completed_sessions
    report["overall"] = {
        "completed": completed_sessions,
        "failed": failed_sessions,
        "total": total_sessions,
        "completion_ratio": round(completed_sessions / total_sessions, 2) if total_sessions else 0,
        "failure_ratio": round(failed_sessions / total_sessions, 2) if total_sessions else 0,
    }

    filename = f"session_ratio_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    logging.info("Session ratio report saved")
    return report

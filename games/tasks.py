from celery import shared_task
from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils.timezone import now

from .models import Game, GameSession
import logging
import os
import json

logger = logging.getLogger(__name__)

REPORTS_DIR = "/app/reports/"
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
            GameSession.objects.filter(game=game, start_datetime__gte=last_month)
            .values("participants__username")
            .annotate(total_score=Sum("results__score"))
        )
        report[game.name] = {"participants": list(participants)}
    filename = f"monthly_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    logger.info("Monthly Reports: %s", report)
    return report


@shared_task
def generate_session_ratio():
    report = {}
    clear_reports("session_ratio_")
    for game in Game.objects.all():
        sessions_qs = game.sessions.all()
        total_sessions = sessions_qs.count()
        completed_sessions = game.sessions.filter(results__is_completed=True).count()
        failed_sessions = total_sessions - completed_sessions
        completion_ratio = completed_sessions / total_sessions if total_sessions else 0
        failure_ratio = failed_sessions / total_sessions if total_sessions else 0
        report[game.name] = {
            "completed": completed_sessions,
            "failed": failed_sessions,
            "total": total_sessions,
            "completion_ratio": round(completion_ratio, 2),
            "failure_ratio": round(failure_ratio, 2),
        }
    filename = f"session_ratio_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    logger.info("Session Completion Ratio: %s", report)
    return report

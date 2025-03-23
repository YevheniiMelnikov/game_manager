from celery import shared_task
from datetime import datetime, timedelta
from django.db.models import Sum
from .models import Game, GameSession
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_monthly_reports():
    last_month = datetime.now() - timedelta(days=30)
    report = []

    games = Game.objects.all()
    for game in games:
        participants = (
            GameSession.objects.filter(game=game, start_datetime__gte=last_month)
            .values("participants__username")
            .annotate(total_score=Sum("results__score"))
        )

        report.append({"game": game.name, "participants": list(participants)})

    logger.info("Monthly Reports: %s", report)
    return report


@shared_task
def generate_session_ratio():
    total_sessions = GameSession.objects.count()
    completed_sessions = GameSession.objects.filter(is_completed=True).count()
    failed_sessions = GameSession.objects.filter(is_completed=False).count()

    ratio = {
        "completed": completed_sessions,
        "failed": failed_sessions,
        "total": total_sessions,
        "completion_ratio": completed_sessions / total_sessions if total_sessions > 0 else 0,
        "failure_ratio": failed_sessions / total_sessions if total_sessions > 0 else 0,
    }

    logger.info("Session Completion Ratio: %s", ratio)
    return ratio

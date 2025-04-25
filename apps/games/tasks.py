import os
import json
from datetime import datetime, timedelta
from typing import Any

from celery import shared_task
from django.db import transaction, connection
from django.db.models import Sum, Count, Q
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Game, GameSession, GameResults

User = get_user_model()
REPORTS_DIR = os.path.join(settings.BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def save_report(filename: str, data: dict) -> None:
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def get_last_month_range():
    first_current = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_prev = first_current - timedelta(days=1)
    first_last = last_prev.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_last = last_prev.replace(hour=23, minute=59, second=59, microsecond=999999)
    return first_last, last_last


@shared_task
def generate_monthly_reports() -> dict[str, Any]:
    start, end = get_last_month_range()
    report: dict[str, Any] = {}

    for game in Game.objects.all():
        parts = (
            GameResults.objects.filter(
                game_session__game=game,
                game_session__start_datetime__gte=start,
                game_session__start_datetime__lte=end,
            )
            .values("game_session__participants__id", "game_session__participants__username")
            .annotate(total_score=Sum("score"))
        )
        report[game.name] = {"participants": list(parts)}

    filename = f"monthly_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    return report


@shared_task
def generate_session_ratio() -> dict[str, Any]:
    report: dict[str, Any] = {
        "by_game": {g.name: g.get_session_metrics() for g in Game.objects.all()},
        "by_participant": {u.username: u.get_sessions_metrics() for u in User.objects.all()},
    }

    agg = GameSession.objects.aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(results__is_completed=True, results__isnull=False)),
    )
    total, completed = agg["total"], agg["completed"]
    failed = total - completed
    report["overall"] = {
        "total": total,
        "completed": completed,
        "failed": failed,
        "completion_ratio": round(completed / total, 2) if total else 0,
        "failure_ratio": round(failed / total, 2) if total else 0,
    }

    filename = f"session_ratio_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    return report


@shared_task
def generate_monthly_reports_raw() -> dict[str, Any]:
    start, end = get_last_month_range()
    report: dict[str, Any] = {}

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT g.name,
                   u.id,
                   u.username,
                   SUM(gr.score)
            FROM games_game g
            JOIN games_gamesession gs          ON gs.game_id = g.id
            JOIN games_gameresults gr          ON gr.game_session_id = gs.id
            JOIN games_gamesession_participants gp ON gp.gamesession_id = gs.id
            JOIN games_customuser u            ON u.id = gp.customuser_id
            WHERE gs.start_datetime BETWEEN %s AND %s
            GROUP BY g.name, u.id, u.username
            """,
            [start, end],
        )
        for game_name, user_id, username, total in cursor.fetchall():
            report.setdefault(game_name, {"participants": []})["participants"].append(
                {
                    "game_session__participants__id": user_id,
                    "game_session__participants__username": username,
                    "total_score": total,
                }
            )

    filename = f"monthly_report_raw_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    return report


@shared_task
def generate_session_ratio_raw() -> dict[str, Any]:
    report: dict[str, Any] = {}
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT g.name,
                   COUNT(DISTINCT gs.id)                                     AS total,
                   COUNT(DISTINCT CASE WHEN gr.is_completed IS TRUE THEN gs.id END) AS completed
            FROM games_game g
            JOIN games_gamesession gs ON gs.game_id = g.id
            LEFT JOIN games_gameresults gr ON gr.game_session_id = gs.id
            GROUP BY g.name
            """
        )
        report["by_game"] = {}
        for name, total, completed in cursor.fetchall():
            failed = total - completed
            report["by_game"][name] = {
                "total": total,
                "completed": completed,
                "failed": failed,
                "completion_ratio": round(completed / total, 2) if total else 0,
                "failure_ratio": round(failed / total, 2) if total else 0,
            }

        cursor.execute(
            """
            SELECT u.username,
                   COUNT(DISTINCT gs.id)                                     AS total,
                   COUNT(DISTINCT CASE WHEN gr.is_completed IS TRUE THEN gs.id END) AS completed
            FROM games_customuser u
            JOIN games_gamesession_participants gp ON gp.customuser_id = u.id
            JOIN games_gamesession gs ON gs.id = gp.gamesession_id
            LEFT JOIN games_gameresults gr ON gr.game_session_id = gs.id
            GROUP BY u.username
            """
        )
        report["by_participant"] = {}
        for username, total, completed in cursor.fetchall():
            failed = total - completed
            report["by_participant"][username] = {
                "total": total,
                "completed": completed,
                "failed": failed,
                "completion_ratio": round(completed / total, 2) if total else 0,
                "failure_ratio": round(failed / total, 2) if total else 0,
            }

        cursor.execute(
            """
            SELECT COUNT(DISTINCT gs.id)                                     AS total,
                   COUNT(DISTINCT CASE WHEN gr.is_completed IS TRUE THEN gs.id END) AS completed
            FROM games_gamesession gs
            LEFT JOIN games_gameresults gr ON gr.game_session_id = gs.id
            """
        )
        total, completed = cursor.fetchone()
        failed = total - completed
        report["overall"] = {
            "total": total,
            "completed": completed,
            "failed": failed,
            "completion_ratio": round(completed / total, 2) if total else 0,
            "failure_ratio": round(failed / total, 2) if total else 0,
        }

    filename = f"session_ratio_raw_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    return report

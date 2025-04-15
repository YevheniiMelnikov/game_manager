from celery import shared_task
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import get_user_model
from games.models import Game, GameSession, GameResults
import os
import json
from typing import Any

User = get_user_model()
REPORTS_DIR = os.path.join(settings.BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def save_report(filename: str, data: dict[str, Any]) -> None:
    file_path = os.path.join(REPORTS_DIR, filename)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def get_last_month_range() -> (datetime, datetime):
    first_day_current_month = now().replace(day=1, hour=0, minute=0, second=0)
    last_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_last_month = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0)
    last_day_last_month = last_day_prev_month.replace(hour=23, minute=59, second=59)
    return first_day_last_month, last_day_last_month


@shared_task
def generate_monthly_reports() -> dict[str, Any]:
    start_date, end_date = get_last_month_range()
    report = dict()
    for game in Game.objects.all():
        participants = (
            GameResults.objects.filter(
                game_session__game=game,
                game_session__start_datetime__gte=start_date,
                game_session__start_datetime__lte=end_date,
            )
            .values("game_session__participants__id", "game_session__participants__username")
            .annotate(total_score=Sum("score"))
        )
        report[game.name] = {"participants": list(participants)}
    filename = f"monthly_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    return report


@shared_task
def generate_session_ratio() -> dict[str, Any]:
    report = dict()
    report["by_game"] = {game.name: game.get_session_metrics() for game in Game.objects.all()}
    report["by_participant"] = {user.username: user.get_session_metrics() for user in User.objects.all()}

    sessions: dict = GameSession.objects.aggregate(
        total=Count("id"),
        completed=Count(
            "id",
            filter=Q(
                results__is_completed=True,
                results__isnull=False,
            ),
        ),
    )
    total_sessions = sessions["total"]
    completed_sessions = sessions["completed"]
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
    return report


@shared_task
def generate_monthly_reports_raw() -> dict[str, Any]:
    start_date, end_date = get_last_month_range()
    report = dict()
    from django.db import connection, transaction

    with transaction.atomic():
        with connection.cursor() as cursor:
            query = """
            SELECT g.name as game_name, u.id as user_id, u.username, SUM(gr.score) as total_score
            FROM games_game g
            JOIN games_gamesession gs ON gs.game_id = g.id
            JOIN games_gameresults gr ON gr.game_session_id = gs.id
            JOIN games_gamesession_participants gsp ON gs.id = gsp.gamesession_id
            JOIN games_customuser u ON gsp.customuser_id = u.id
            WHERE gs.start_datetime BETWEEN %s AND %s
            GROUP BY g.name, u.id, u.username
            ORDER BY g.name
            """
            cursor.execute(query, [start_date, end_date])
            rows = cursor.fetchall()
            for row in rows:
                game_name, user_id, username, total_score = row
                if game_name not in report:
                    report[game_name] = {"participants": []}
                report[game_name]["participants"].append(
                    {
                        "game_session__participants__id": user_id,
                        "game_session__participants__username": username,
                        "total_score": total_score,
                    }
                )
    filename = f"monthly_report_raw_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    return report


@shared_task
def generate_session_ratio_raw() -> dict[str, Any]:
    report = dict()
    from django.db import connection, transaction

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT g.name, COUNT(DISTINCT gs.id) as total,
                   COUNT(DISTINCT CASE WHEN gr.is_completed = 1 THEN gs.id END) as completed
            FROM games_game g
            JOIN games_gamesession gs ON gs.game_id = g.id
            LEFT JOIN games_gameresults gr ON gs.id = gr.game_session_id
            GROUP BY g.name
            """)  # by game
            games_metrics = cursor.fetchall()
            report["by_game"] = {}
            for row in games_metrics:
                game_name, total, completed = row
                failed = total - completed
                report["by_game"][game_name] = {
                    "total": total,
                    "completed": completed,
                    "failed": failed,
                    "completion_ratio": round(completed / total, 2) if total else 0,
                    "failure_ratio": round(failed / total, 2) if total else 0,
                }
            cursor.execute("""
            SELECT u.username, COUNT(DISTINCT gs.id) as total,
                   COUNT(DISTINCT CASE WHEN gr.is_completed = 1 THEN gs.id END) as completed
            FROM games_customuser u
            JOIN games_gamesession_participants gsp ON u.id = gsp.customuser_id
            JOIN games_gamesession gs ON gs.id = gsp.gamesession_id
            LEFT JOIN games_gameresults gr ON gs.id = gr.game_session_id
            GROUP BY u.username
            """)  # by participant
            participants_metrics = cursor.fetchall()
            report["by_participant"] = {}
            for row in participants_metrics:
                username, total, completed = row
                failed = total - completed
                report["by_participant"][username] = {
                    "total": total,
                    "completed": completed,
                    "failed": failed,
                    "completion_ratio": round(completed / total, 2) if total else 0,
                    "failure_ratio": round(failed / total, 2) if total else 0,
                }
            cursor.execute("""
            SELECT COUNT(DISTINCT gs.id) as total,
                   COUNT(DISTINCT CASE WHEN gr.is_completed = 1 THEN gs.id END) as completed
            FROM games_gamesession gs
            LEFT JOIN games_gameresults gr ON gs.id = gr.game_session_id
            """)  # general report
            row = cursor.fetchone()
            total, completed = row
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

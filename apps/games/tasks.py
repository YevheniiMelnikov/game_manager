import os
import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.db.models import Count, Q, Sum
from django.utils.timezone import now

from .models import Game, GameSession, GameResults
from .schemas import SessionMetrics, ParticipantReport, GameReport

User = get_user_model()
USER_TABLE = User._meta.db_table
USER_PK_COL = f"{User._meta.model_name}_id"
REPORTS_DIR = os.path.join(settings.BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def last_month_range() -> Tuple[datetime, datetime]:
    first_day_this_month = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start = first_day_this_month - relativedelta(months=1)
    end = first_day_this_month - timedelta(microseconds=1)
    return start, end


def save_report(name: str, data: Dict[str, Any]) -> None:
    path = os.path.join(REPORTS_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)


def _current_timestamp() -> str:
    return now().strftime("%Y%m%d%H%M%S")


@shared_task
def generate_monthly_reports() -> Dict[str, Any]:
    start, end = last_month_range()
    rows = (
        GameResults.objects.filter(game_session__start_datetime__range=(start, end))
        .values(
            "game_session__game__name",
            "game_session__participants__id",
            "game_session__participants__username",
        )
        .annotate(total_score=Sum("score"))
    )

    report: Dict[str, GameReport] = defaultdict(lambda: GameReport(participants=[]))
    for row in rows:
        game_name = row.pop("game_session__game__name")
        report[game_name].participants.append(ParticipantReport(**row))

    result = {k: v.dict() for k, v in report.items()}
    save_report(f"monthly_report_{_current_timestamp()}.json", result)
    return result


@shared_task
def generate_session_ratio() -> Dict[str, Any]:
    report = {
        "by_game": {g.name: g.get_session_metrics().dict() for g in Game.objects.all()},
        "by_participant": {u.username: u.get_sessions_metrics().dict() for u in User.objects.all()},
    }

    agg = GameSession.objects.aggregate(
        total=Count("id"), completed=Count("id", filter=Q(results__is_completed=True, results__isnull=False))
    )

    total = agg["total"] or 0
    completed = agg["completed"] or 0
    failed = total - completed

    report["overall"] = SessionMetrics(
        completed=completed,
        failed=failed,
        total=total,
        completion_ratio=round(completed / total, 2) if total else 0,
        failure_ratio=round(failed / total, 2) if total else 0,
    ).dict()

    save_report(f"session_ratio_{_current_timestamp()}.json", report)
    return report


@shared_task
def generate_monthly_reports_raw() -> Dict[str, Any]:
    start, end = last_month_range()
    report: Dict[str, GameReport] = {}

    query = f"""
        SELECT g.name, u.id, u.username, SUM(gr.score)
        FROM games_game g
        JOIN games_gamesession gs ON gs.game_id = g.id
        JOIN games_gameresults gr ON gr.game_session_id = gs.id
        JOIN games_gamesession_participants gp ON gp.gamesession_id = gs.id
        JOIN {USER_TABLE} u ON u.id = gp.{USER_PK_COL}
        WHERE gs.start_datetime BETWEEN %s AND %s
        GROUP BY g.name, u.id, u.username
    """

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(query, [start, end])
        for game_name, user_id, username, total_score in cursor.fetchall():
            report.setdefault(game_name, GameReport(participants=[])).participants.append(
                ParticipantReport(
                    game_session__participants__id=user_id,
                    game_session__participants__username=username,
                    total_score=total_score,
                )
            )

    result = {k: v.dict() for k, v in report.items()}
    save_report(f"monthly_report_raw_{_current_timestamp()}.json", result)
    return result


@shared_task
def generate_session_ratio_raw() -> Dict[str, Any]:
    report: Dict[str, Any] = {}

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("""
            SELECT g.name,
                   COUNT(DISTINCT gs.id) AS total,
                   COUNT(DISTINCT CASE WHEN gr.is_completed IS TRUE THEN gs.id END) AS completed
            FROM games_game g
            JOIN games_gamesession gs ON gs.game_id = g.id
            LEFT JOIN games_gameresults gr ON gr.game_session_id = gs.id
            GROUP BY g.name
        """)

        # by game
        report["by_game"] = {}
        for name, total, completed in cursor.fetchall():
            failed = total - completed
            report["by_game"][name] = SessionMetrics(
                total=total,
                completed=completed,
                failed=failed,
                completion_ratio=round(completed / total, 2) if total else 0,
                failure_ratio=round(failed / total, 2) if total else 0,
            ).dict()

        cursor.execute(f"""
            SELECT u.username,
                   COUNT(DISTINCT gs.id) AS total,
                   COUNT(DISTINCT CASE WHEN gr.is_completed IS TRUE THEN gs.id END) AS completed
            FROM {USER_TABLE} u
            JOIN games_gamesession_participants gp ON gp.{USER_PK_COL} = u.id
            JOIN games_gamesession gs ON gs.id = gp.gamesession_id
            LEFT JOIN games_gameresults gr ON gr.game_session_id = gs.id
            GROUP BY u.username
        """)

        # by participant
        report["by_participant"] = {}
        for username, total, completed in cursor.fetchall():
            failed = total - completed
            report["by_participant"][username] = SessionMetrics(
                total=total,
                completed=completed,
                failed=failed,
                completion_ratio=round(completed / total, 2) if total else 0,
                failure_ratio=round(failed / total, 2) if total else 0,
            ).dict()

        cursor.execute("""
            SELECT COUNT(DISTINCT gs.id) AS total,
                   COUNT(DISTINCT CASE WHEN gr.is_completed IS TRUE THEN gs.id END) AS completed
            FROM games_gamesession gs
            LEFT JOIN games_gameresults gr ON gr.game_session_id = gs.id
        """)

        # overall
        total, completed = cursor.fetchone()
        failed = total - completed
        report["overall"] = SessionMetrics(
            total=total,
            completed=completed,
            failed=failed,
            completion_ratio=round(completed / total, 2) if total else 0,
            failure_ratio=round(failed / total, 2) if total else 0,
        ).dict()

    save_report(f"session_ratio_raw_{_current_timestamp()}.json", report)
    return report

from typing import Any, Dict

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.db.models import Count, Q
from django.utils.timezone import now
from loguru import logger

from .models import Game, GameSession
from .schemas import ParticipantReport, GameReport
from .utils import last_month_range, save_report, make_metrics

User = get_user_model()
USER_TABLE = User._meta.db_table
USER_PK_COL = f"{User._meta.model_name}_id"


@shared_task
def generate_session_ratio() -> Dict[str, Any]:
    # collect session statistics per game and user with ORM
    report = {
        "by_game": {g.name: g.get_session_metrics().dict() for g in Game.objects.all()},
        "by_participant": {
            u.username: u.get_sessions_metrics().dict()
            for u in User.objects.annotate(s=Count("game_sessions")).filter(s__gt=0)
        },
    }

    # aggregate overall session stats across all sessions
    sessions = GameSession.objects.aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(results__is_completed=True, results__isnull=False)),
    )
    report["overall"] = make_metrics(sessions["total"] or 0, sessions["completed"] or 0).dict()
    # save the report to disk
    filename = f"session_ratio_{now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, report)
    logger.success(f"generate_session_ratio completed → {filename}")
    return report


@shared_task
def generate_monthly_reports() -> Dict[str, Any]:
    # calculate scores of participants per game for the past month with raw SQL
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

    # run raw SQL transactionally
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(query, [start, end])
        for game_name, user_id, username, total_score in cursor.fetchall():
            report.setdefault(game_name, GameReport(participants=[])).participants.append(
                ParticipantReport(
                    game_session_participants_id=user_id,
                    game_session_participants_username=username,
                    total_score=total_score,
                )
            )

    result = {k: v.dict() for k, v in report.items()}
    # save the report to disk
    filename = f"monthly_report_{now().strftime('%Y%m%d%H%M%S')}.json"
    save_report(filename, result)
    logger.success(f"generate_monthly_reports completed → {filename}")
    return result

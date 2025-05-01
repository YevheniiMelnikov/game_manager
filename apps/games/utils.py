import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Dict, Any

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils.timezone import now

from apps.games.schemas import SessionMetrics
from config.settings import BASE_DIR

REPORTS_DIR: Path = Path(settings.BASE_DIR) / "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


def last_month_range() -> Tuple[datetime, datetime]:
    first_day = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return first_day - relativedelta(months=1), first_day - timedelta(microseconds=1)


def save_report(filename: str, data: Dict[str, Any]) -> None:
    REPORTS_DIR = BASE_DIR / "reports"
    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / filename
    print(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True, default=str)


def make_metrics(total: int, completed: int) -> SessionMetrics:
    failed = total - completed
    return SessionMetrics(
        total=total,
        completed=completed,
        failed=failed,
        completion_ratio=round(completed / total, 2) if total else 0,
        failure_ratio=round(failed / total, 2) if total else 0,
    )

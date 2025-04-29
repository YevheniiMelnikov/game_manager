from pydantic import BaseModel
from typing import List


class SessionMetrics(BaseModel):
    completed: int
    failed: int
    total: int
    completion_ratio: float
    failure_ratio: float


class ParticipantReport(BaseModel):
    game_session__participants__id: int
    game_session__participants__username: str
    total_score: int


class GameReport(BaseModel):
    participants: List[ParticipantReport]


class FullSessionReport(BaseModel):
    by_game: dict[str, SessionMetrics]
    by_participant: dict[str, SessionMetrics]
    overall: SessionMetrics

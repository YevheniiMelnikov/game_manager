from enum import Enum


class DjangoChoicesEnum(Enum):
    @classmethod
    def choices(cls):
        return [(tag.value, tag.name) for tag in cls]


class GameCategory(str, DjangoChoicesEnum):
    ACTION = "Action"
    PUZZLE = "Puzzle"
    STRATEGY = "Strategy"


class GameSessionStatus(str, DjangoChoicesEnum):
    CREATED = "Created"
    IN_PROGRESS = "InProgress"
    FINISHED = "Finished"
    FAILED = "Failed"

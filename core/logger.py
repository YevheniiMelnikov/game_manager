import logging
import sys
from loguru import logger

from core.settings import Settings


logger.remove()
logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "level": Settings.DJANGO_LOG_LEVEL,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",  # noqa
            "colorize": True,
        },
        {
            "sink": "game_management.log",
            "level": "INFO",
            "serialize": False,
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            "rotation": "100 MB",
            "retention": "30 days",
            "compression": "zip",
            "enqueue": True,
        },
    ]
)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            loguru_level = logger.level(record.levelname).name
        except Exception:
            loguru_level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(loguru_level, record.getMessage())

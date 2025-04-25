import sys

from loguru import logger

from config.env_settings import Settings

logger.remove()
logger.configure(
    handlers=[  # type: ignore
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

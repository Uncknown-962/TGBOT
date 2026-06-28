import sys
from pathlib import Path
from loguru import logger

from config.settings import settings


def setup_logger():
    log_dir = Path(__file__).resolve().parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )

    logger.add(
        log_dir / 'bot_{time:YYYY-MM-DD}.log',
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=settings.LOG_LEVEL,
        rotation="00:00",
        retention="30 days",
        compression="zip"
    )

    return logger


log = setup_logger()

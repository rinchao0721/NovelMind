"""
Logger Utility using loguru
Configures application-wide logging to file and console with rotation and structured logging
"""

import sys
import logging
from pathlib import Path
from loguru import logger

# Log directory
LOG_DIR = Path("data")
LOG_FILE = LOG_DIR / "app.log"


class InterceptHandler(logging.Handler):
    """Intercept standard logging messages and redirect to loguru"""

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logger():
    """Configure the loguru logger"""
    # Ensure log directory exists
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Format
    # Time | Level | Module:Function:Line - Message
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Console Handler
    logger.add(
        sys.stdout,
        format=log_format,
        level="INFO",
        colorize=True,
    )

    # File Handler (Rotate at 5MB, keep 5 backups)
    logger.add(
        LOG_FILE,
        format=log_format,
        level="INFO",
        rotation="5 MB",
        retention=5,
        encoding="utf-8",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # Configure standard logging to use InterceptHandler
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Silence noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)

    logger.info("Loguru initialized successfully - Logger operational")

    return logger


def get_log_file_path() -> Path:
    return LOG_FILE

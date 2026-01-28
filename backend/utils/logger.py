"""
Logger Utility
Configures application-wide logging to file and console
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Log directory
LOG_DIR = Path("data")
LOG_FILE = LOG_DIR / "app.log"


def setup_logger():
    """Configure the root logger"""
    # Ensure log directory exists
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File Handler (Rotate at 5MB, keep 3 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Add handlers
    # Remove existing handlers to avoid duplicates during reloads
    logger.handlers = []
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Silence noisy libraries
    logging.getLogger(
        "uvicorn.access"
    ).handlers = []  # We handle this via root logger or let it propagate
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)

    return logger


def get_log_file_path() -> Path:
    return LOG_FILE

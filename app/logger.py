import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from termcolor import colored

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log file path with timestamp
LOG_FILE = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"


class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to levelname field for console output only"""

    COLORS = {
        "DEBUG": "grey",
        "INFO": "blue",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red",
    }

    def __init__(self, *args, use_colors=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_colors = use_colors

    def format(self, record):
        # Only color the log level name if colors are enabled
        if self.use_colors:
            levelname = record.levelname
            if levelname in self.COLORS:
                colored_levelname = colored(levelname, self.COLORS[levelname])
                # Store the original levelname
                original_levelname = record.levelname
                record.levelname = colored_levelname
                # Format the record
                result = super().format(record)
                # Restore the original levelname
                record.levelname = original_levelname
                return result
        return super().format(record)


def setup_logger(name: str = "app", level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with both console and file handlers.

    Args:
        name (str): Name of the logger
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent propagation to root logger to avoid double logging
    logger.propagate = False

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        use_colors=True,
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with plain formatting (no colors)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(level)
    file_formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        use_colors=False,
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


# Create default logger instance
logger = setup_logger()


def get_logger(
    name: Optional[str] = None, level: Optional[str] = None
) -> logging.Logger:
    """
    Get a logger instance. If name is None, returns the default logger.

    Args:
        name (str, optional): Name of the logger
        level (str, optional): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        return logger

    return setup_logger(name, level or "INFO")

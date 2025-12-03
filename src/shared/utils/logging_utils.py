"""Logging utilities for centralized configuration."""

import logging
import os
from typing import Optional

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_LOG_FILE = os.path.join(os.getcwd(), "data", "logs", "log.txt")


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Configure root logger with console + file handlers.

    Args:
        level: Logging level to use (default: INFO)
        log_file: Optional custom log file path (default: ./log.txt)
    """
    log_path = log_file or DEFAULT_LOG_FILE
    root_logger = logging.getLogger()

    # Reset existing handlers to avoid duplicate logs during repeated setup calls
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # Ensure directory exists before creating file handler
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Convenience helper to fetch module-level loggers.

    Args:
        name: Logger name. Defaults to module name via __name__ when None.

    Returns:
        Configured Logger instance.
    """
    return logging.getLogger(name or __name__)


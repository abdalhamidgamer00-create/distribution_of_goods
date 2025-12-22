"""Logging utilities for centralized configuration."""

import logging
import os
from typing import Optional


# =============================================================================
# CONSTANTS
# =============================================================================

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_LOG_FILE = os.path.join(os.getcwd(), "data", "logs", "log.txt")


# =============================================================================
# PUBLIC API
# =============================================================================

def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Configure root logger with console + file handlers."""
    log_path = log_file or DEFAULT_LOG_FILE
    root_logger = logging.getLogger()
    
    _reset_handlers(root_logger)
    root_logger.setLevel(level)
    
    formatter = logging.Formatter(LOG_FORMAT)
    root_logger.addHandler(_create_console_handler(formatter))
    root_logger.addHandler(_create_file_handler(log_path, formatter))


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Convenience helper to fetch module-level loggers.

    Args:
        name: Logger name. Defaults to module name via __name__ when None.

    Returns:
        Configured Logger instance.
    """
    return logging.getLogger(name or __name__)


# =============================================================================
# HANDLER MANAGEMENT HELPERS
# =============================================================================

def _reset_handlers(logger: logging.Logger) -> None:
    """Remove all existing handlers from logger."""
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)


def _create_console_handler(formatter: logging.Formatter) -> logging.Handler:
    """Create and configure console handler."""
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    return stream_handler


def _create_file_handler(log_path: str, formatter: logging.Formatter) -> logging.Handler:
    """Create and configure file handler."""
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    return file_handler

"""Logging helpers for step execution."""

from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


from typing import Any

def log_step_header(step_index: int, total: int, step: Any) -> None:
    """Log step execution header."""
    logger.info("")
    logger.info("[%d/%d] Executing: %s", step_index, total, step.name)
    logger.info("-" * 70)


def log_step_failure(step: Any) -> None:
    """Log step failure message."""
    logger.error("")
    logger.error("✗ FAILED at step %s: %s", step.id, step.name)
    logger.error("Stopping execution. Previous steps completed successfully.")


def log_success_banner(steps_count: int) -> None:
    """Log success banner for completed steps."""
    logger.info("")
    logger.info("=" * 70)
    logger.info(
        "✓ SUCCESS: All %d steps completed successfully!", steps_count
    )
    logger.info("=" * 70)

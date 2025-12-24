"""Single step execution logic."""

from src.shared.utility.logging_utils import get_logger
from src.presentation.cli.executors.step_executor.lookup import validate_step_function

from typing import Any

logger = get_logger(__name__)


def handle_step_result(step: Any, success: bool) -> bool:
    """Log step result and return success status."""
    if success:
        logger.info("✓ Step %s completed successfully", step.id)
    else:
        logger.error("✗ Step %s failed", step.id)
    return success


def execute_single_step(step: Any, use_latest_file: bool = False) -> bool:
    """Execute a single step with error handling."""
    if not validate_step_function(step):
        logger.error("✗ Step %s has no valid function!", step.id)
        return False
    try:
        return handle_step_result(
            step, step.function(use_latest_file=use_latest_file)
        )
    except Exception as error:
        logger.exception("✗ Step %s crashed: %s", step.id, error)
        return False

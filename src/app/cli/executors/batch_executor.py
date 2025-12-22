"""Batch step execution"""

from src.app.pipeline.steps import AVAILABLE_STEPS
from src.app.cli.core.constants import SEPARATOR
from src.app.cli.handlers.input_handler import get_file_selection_mode
from src.app.cli.executors.step_executor import execute_single_step
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def log_step_progress(step: dict, current: int, total: int) -> None:
    """Log current step progress."""
    logger.info("[%d/%d] %s - %s", current, total, step["id"], step["name"])
    logger.info("-" * 50)


def _execute_and_track(step: dict, use_latest_file: bool) -> bool:
    """Execute a step and track its result."""
    success = execute_single_step(step, use_latest_file)
    step['_last_result'] = success
    return success


def execute_all_steps_batch(use_latest_file: bool) -> tuple[int, int]:
    """Execute all steps and return success/failure counts."""
    total_steps = len(AVAILABLE_STEPS)
    successful_count = 0
    
    for idx, step in enumerate(AVAILABLE_STEPS, 1):
        log_step_progress(step, idx, total_steps)
        if _execute_and_track(step, use_latest_file):
            successful_count += 1
    
    return successful_count, total_steps


def display_execution_summary(successful: int, total: int) -> None:
    """Display final execution statistics."""
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0
    logger.info(SEPARATOR + "\nExecution Summary:\n  Total steps: %d\n  Successful: %d\n  Failed: %d\n  Success rate: %.1f%%\n" + SEPARATOR, total, successful, failed, success_rate)


def _run_steps_with_mode(use_latest: bool) -> bool:
    """Run all steps with the given file selection mode."""
    if use_latest:
        logger.info("Using latest file for all steps...")
    try:
        successful, total = execute_all_steps_batch(use_latest)
        display_execution_summary(successful, total)
        return successful == total
    except Exception as e:
        logger.exception("Error during batch execution: %s", e); return False


def execute_all_steps() -> bool:
    """Execute all steps in order with user file selection."""
    logger.info("Executing all steps...")
    logger.info(SEPARATOR)
    
    use_latest = get_file_selection_mode()
    if use_latest is None:
        return False
    
    return _run_steps_with_mode(use_latest)


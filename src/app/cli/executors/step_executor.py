"""Single step execution"""

from typing import Optional
from src.app.pipeline.steps import AVAILABLE_STEPS
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def find_step_by_id(step_id: str) -> Optional[dict]:
    """Find a step by its ID."""
    return next((s for s in AVAILABLE_STEPS if s['id'] == step_id), None)


def validate_step_function(step: dict) -> bool:
    """Check if step has a valid callable function."""
    return callable(step.get('function'))


def _handle_step_result(step: dict, success: bool) -> bool:
    """Log step result and return success status."""
    if success:
        logger.info("✓ Step %s completed successfully", step["id"])
    else:
        logger.error("✗ Step %s failed", step["id"])
    return success


def execute_single_step(step: dict, use_latest_file: bool = False) -> bool:
    """Execute a single step with error handling."""
    if not validate_step_function(step):
        logger.error("✗ Step %s has no valid function!", step["id"])
        return False
    
    try:
        success = step['function'](use_latest_file=use_latest_file)
        return _handle_step_result(step, success)
    except Exception as e:
        logger.exception("✗ Step %s crashed: %s", step["id"], e)
        return False


def execute_step(step_id: str) -> bool:
    """Execute a single step by ID."""
    step = find_step_by_id(step_id)
    
    if step is None:
        logger.error("Error: Invalid step number!")
        return False
    
    logger.info("Executing: %s", step["name"])
    logger.info("-" * 50)
    
    return execute_single_step(step, use_latest_file=False)


def _get_steps_up_to(step_id: str) -> list:
    """Get all steps up to and including the target step ID."""
    try:
        target_step_num = int(step_id)
    except ValueError:
        return []
    
    return [s for s in AVAILABLE_STEPS if int(s['id']) <= target_step_num]


def _log_step_header(idx: int, total: int, step: dict) -> None:
    """Log step execution header."""
    logger.info("")
    logger.info("[%d/%d] Executing: %s", idx, total, step["name"])
    logger.info("-" * 70)


def _log_step_failure(step: dict) -> None:
    """Log step failure message."""
    logger.error("")
    logger.error("✗ FAILED at step %s: %s", step['id'], step['name'])
    logger.error("Stopping execution. Previous steps completed successfully.")


def _run_step_sequence(all_steps: list) -> bool:
    """Run a sequence of steps, stopping on first failure."""
    for idx, step in enumerate(all_steps, 1):
        _log_step_header(idx, len(all_steps), step)
        
        if not execute_single_step(step, use_latest_file=False):
            _log_step_failure(step)
            return False
        logger.info("✓ Step %s completed", step['id'])
    
    return True


def _log_success_banner(steps_count: int) -> None:
    """Log success banner for completed steps."""
    logger.info("")
    logger.info("=" * 70)
    logger.info("✓ SUCCESS: All %d steps completed successfully!", steps_count)
    logger.info("=" * 70)


def execute_step_with_dependencies(step_id: str) -> bool:
    """Execute all steps from 1 to step_id in sequence."""
    all_steps = _get_steps_up_to(step_id)
    
    if not all_steps:
        logger.error("✗ No steps found up to step %s", step_id)
        return False
    
    logger.info("=" * 70)
    logger.info("Running steps 1 through %s (Total: %d steps)", step_id, len(all_steps))
    logger.info("=" * 70)
    
    success = _run_step_sequence(all_steps)
    if success:
        _log_success_banner(len(all_steps))
    return success

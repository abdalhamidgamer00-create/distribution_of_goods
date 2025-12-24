"""Sequential step execution logic."""

from src.shared.utils.logging_utils import get_logger
from .step_execution import execute_single_step
from .logging import (
    log_step_header,
    log_step_failure
)

logger = get_logger(__name__)


def run_step_sequence(all_steps: list, use_latest_file: bool = False) -> bool:
    """Run a sequence of steps, stopping on first failure."""
    for step_index, step in enumerate(all_steps, 1):
        log_step_header(step_index, len(all_steps), step)
        
        if not execute_single_step(step, use_latest_file=use_latest_file):
            log_step_failure(step)
            return False
        logger.info("✓ Step %s completed", step.id)
    
    return True

"""Main orchestration for step execution."""

from src.shared.utils.logging_utils import get_logger
from src.app.cli.executors.step_executor import lookup
from src.app.cli.executors.step_executor import step_execution as execution
from src.app.cli.executors.step_executor import sequence
from src.app.cli.executors.step_executor import logging

logger = get_logger(__name__)


def run_and_log_success(all_steps: list, use_latest_file: bool = False) -> bool:
    """Run steps and log success if all complete."""
    success = sequence.run_step_sequence(all_steps, use_latest_file=use_latest_file)
    if success:
        logging.log_success_banner(len(all_steps))
    return success


def execute_step(step_id: str, use_latest_file: bool = False) -> bool:
    """Execute a single step by ID."""
    step = lookup.find_step_by_id(step_id)
    if step is None:
        logger.error("Error: Invalid step number!")
        return False
    logger.info("Executing: %s\n" + "-" * 50, step.name)
    return execution.execute_single_step(step, use_latest_file=use_latest_file)


def execute_step_with_dependencies(step_id: str, use_latest_file: bool = False) -> bool:
    """Execute all steps from 1 to step_id in sequence."""
    all_steps = lookup.get_steps_up_to(step_id)
    if not all_steps:
        logger.error("✗ No steps found up to step %s", step_id)
        return False
    
    logger.info("=" * 70)
    logger.info(
        "Running steps 1 through %s (Total: %d steps)", 
        step_id, len(all_steps)
    )
    logger.info("=" * 70)
    return run_and_log_success(all_steps, use_latest_file=use_latest_file)

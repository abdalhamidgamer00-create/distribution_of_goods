"""Main orchestration for step execution."""

from src.shared.utility.logging_utils import get_logger
from src.presentation.cli.executors.step_executor import lookup
from src.presentation.cli.executors.step_executor import step_execution as execution
from src.presentation.cli.executors.step_executor import sequence
from src.presentation.cli.executors.step_executor import logging

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


def execute_step_with_dependencies(
    step_id: str, use_latest_file: bool = False
) -> bool:
    """Execute Step 1 (Archiving) followed by the target step."""
    target_step = lookup.find_step_by_id(step_id)
    if not target_step:
        logger.error("✗ Step %s not found", step_id)
        return False

    if step_id == "1":
        all_steps = [target_step]
    else:
        archive_step = lookup.find_step_by_id("1")
        all_steps = [archive_step, target_step] if archive_step else [target_step]
    
    logger.info("=" * 70)
    if len(all_steps) > 1:
        logger.info(
            "Running Archiving (Step 1) and Target Step (%s: %s)", 
            step_id, target_step.name
        )
    else:
        logger.info("Running Step %s: %s", step_id, target_step.name)
    logger.info("=" * 70)
    
    return run_and_log_success(all_steps, use_latest_file=use_latest_file)

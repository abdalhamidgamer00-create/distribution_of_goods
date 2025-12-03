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


def execute_single_step(step: dict, use_latest_file: bool = False) -> bool:
    """
    Execute a single step with error handling.
    
    Args:
        step: Step dictionary containing function and metadata
        use_latest_file: Whether to use latest file automatically
        
    Returns:
        True if successful, False otherwise
    """
    if not validate_step_function(step):
        logger.error("✗ Step %s has no valid function!", step["id"])
        return False
    
    try:
        success = step['function'](use_latest_file=use_latest_file)
        
        if success:
            logger.info("✓ Step %s completed successfully", step["id"])
        else:
            logger.error("✗ Step %s failed", step["id"])
        
        return success
        
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


def execute_step_with_dependencies(step_id: str) -> bool:
    """
    Execute all steps from 1 to step_id in sequence.
    
    Args:
        step_id: Target step ID
        
    Returns:
        True if all steps succeeded, False otherwise
    """
    # Get all steps up to target
    try:
        target_step_num = int(step_id)
    except ValueError:
        logger.error("✗ Invalid step ID: %s", step_id)
        return False
    
    all_steps = [s for s in AVAILABLE_STEPS if int(s['id']) <= target_step_num]
    
    if not all_steps:
        logger.error("✗ No steps found up to step %s", step_id)
        return False
    
    logger.info("=" * 70)
    logger.info("Running steps 1 through %s (Total: %d steps)", step_id, len(all_steps))
    logger.info("=" * 70)
    
    for idx, step in enumerate(all_steps, 1):
        logger.info("")
        logger.info("[%d/%d] Executing: %s", idx, len(all_steps), step["name"])
        logger.info("-" * 70)
        
        success = execute_single_step(step, use_latest_file=False)
        
        if not success:
            logger.error("")
            logger.error("✗ FAILED at step %s: %s", step['id'], step['name'])
            logger.error("Stopping execution. Previous steps completed successfully.")
            return False
        
        logger.info("✓ Step %s completed", step['id'])
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("✓ SUCCESS: All %d steps completed successfully!", len(all_steps))
    logger.info("=" * 70)
    
    return True

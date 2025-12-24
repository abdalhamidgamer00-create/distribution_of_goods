"""Pipeline step execution logic for the GUI."""

from typing import Tuple, Any
from src.app.pipeline.steps import AVAILABLE_STEPS
from src.app.gui.utils.translations import STEP_NAMES, MESSAGES
from src.shared.config.paths import (
    RENAMED_CSV_DIR, ANALYTICS_DIR, SURPLUS_DIR, 
    SHORTAGE_DIR, TRANSFERS_CSV_DIR
)


def run_single_step(step_id: str) -> Tuple[bool, str]:
    """Execute a single step and return status and message."""
    step = _find_step_by_id(step_id)
    if not step:
        return False, f"خطوة غير موجودة: {step_id}"
    
    step_name = STEP_NAMES.get(step_id, step.name)
    try:
        # Execute the step with standard parameters
        result = step.function(use_latest_file=True)
        
        status_key = 'success' if result else 'failed'
        return result, f"{MESSAGES[status_key]}: {step_name}"
        
    except Exception as error:
        return False, f"{MESSAGES['error']} في {step_name}: {str(error)}"


def get_repository() -> Any:
    """Get a pre-configured repository instance for the GUI."""
    from src.infrastructure.persistence.pandas_repository import PandasDataRepository
    return PandasDataRepository(
        input_dir=RENAMED_CSV_DIR,
        output_dir=TRANSFERS_CSV_DIR,
        surplus_dir=SURPLUS_DIR,
        shortage_dir=SHORTAGE_DIR,
        analytics_dir=ANALYTICS_DIR
    )


def _find_step_by_id(step_id: str) -> Any:
    """Helper to find a step by its integer ID string."""
    for step in AVAILABLE_STEPS:
        if step.id == step_id:
            return step
    return None

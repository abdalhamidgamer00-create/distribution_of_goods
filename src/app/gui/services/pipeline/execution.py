"""Pipeline step execution logic."""

from typing import Tuple, Dict, Optional, Any
from src.app.pipeline.steps import AVAILABLE_STEPS
from src.app.gui.utils.translations import STEP_NAMES, MESSAGES

def run_single_step(step_id: str) -> Tuple[bool, str]:
    """Execute a single step without UI."""
    step = _find_step_by_id(step_id)
    if not step:
        return False, f"خطوة غير موجودة: {step_id}"
    
    step_name = STEP_NAMES.get(step_id, step.name)
    
    try:
        # Execute pure function
        result = step.function(use_latest_file=True)
        
        if result:
            return True, f"{MESSAGES['success']}: {step_name}"
        return False, f"{MESSAGES['failed']}: {step_name}"
        
    except Exception as error:
        return False, f"{MESSAGES['error']} في {step_name}: {str(error)}"


def _find_step_by_id(step_id: str) -> Any:
    """Find step by its ID."""
    for step in AVAILABLE_STEPS:
        if step.id == step_id:
            return step
    return None


def get_repository() -> Any:
    """Get a pre-configured repository instance for the GUI."""
    from src.infrastructure.persistence.pandas_repository import PandasDataRepository
    return PandasDataRepository(
        input_dir="data/output/converted/renamed",
        output_dir="data/output/transfers",
        surplus_dir="data/output/remaining_surplus",
        shortage_dir="data/output/shortage",
        analytics_dir="data/output/branches/analytics"
    )

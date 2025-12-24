"""Pipeline step sequencing logic."""

from typing import Tuple, Any, List
from src.app.core.steps.steps import AVAILABLE_STEPS

def get_steps_sequence(step_id: str) -> Tuple[bool, Any]:
    """Get sequence of steps up to target step_id."""
    valid, result = _validate_step_id(step_id)
    
    if not valid:
        return False, str(result)
        
    target_step_number = int(result)
    
    steps = [
        step for step in AVAILABLE_STEPS 
        if int(step.id) <= target_step_number
    ]
    
    if not steps:
        return False, f"لم يتم العثور على خطوات حتى الخطوة {step_id}"
        
    return True, steps


def _validate_step_id(step_id: str) -> Tuple[bool, Any]:
    """Validate step_id and return (success, target_step_num/error)."""
    try:
        return True, int(step_id)
    except ValueError:
        return False, f"معرف خطوة غير صالح: {step_id}"

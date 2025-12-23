"""Pipeline execution service."""
import traceback
from typing import Tuple, Optional, Dict, List, Any
from src.app.pipeline.steps import AVAILABLE_STEPS
from src.app.gui.utils.translations import (
    STEP_NAMES, 
    STEP_DESCRIPTIONS,
    MESSAGES
)

# =============================================================================
# PUBLIC API
# =============================================================================

def get_all_steps() -> List[Dict]:
    """Get all available pipeline steps with translations."""
    steps = []
    
    for step in AVAILABLE_STEPS:
        steps.append({
            "id": step["id"],
            "name": STEP_NAMES.get(step["id"], step["name"]),
            "description": STEP_DESCRIPTIONS.get(
                step["id"], 
                step["description"]
            )
        })
        
    return steps


def get_step_info(step_id: str) -> Optional[Dict]:
    """Get information for a specific step."""
    for step in AVAILABLE_STEPS:
        if step["id"] == step_id:
            return _build_step_info(step)
    return None


def run_single_step(step_id: str) -> Tuple[bool, str]:
    """Execute a single step without UI."""
    step = _find_step_by_id(step_id)
    if not step:
        return False, f"خطوة غير موجودة: {step_id}"
    
    step_name = STEP_NAMES.get(step_id, step["name"])
    
    try:
        # Execute pure function
        result = step["function"](use_latest_file=True)
        
        if result:
            return True, f"{MESSAGES['success']}: {step_name}"
        return False, f"{MESSAGES['failed']}: {step_name}"
        
    except Exception as error:
        return False, f"{MESSAGES['error']} في {step_name}: {str(error)}"


def get_steps_sequence(step_id: str) -> Tuple[bool, Any]:
    """Get sequence of steps up to target step_id."""
    valid, result = _validate_step_id(step_id)
    
    if not valid:
        return False, str(result)
        
    target_step_number = int(result)
    
    steps = [
        step for step in AVAILABLE_STEPS 
        if int(step['id']) <= target_step_number
    ]
    
    if not steps:
        return False, f"لم يتم العثور على خطوات حتى الخطوة {step_id}"
        
    return True, steps


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

def _find_step_by_id(step_id: str) -> Optional[Dict]:
    """Find step by its ID."""
    for step in AVAILABLE_STEPS:
        if step["id"] == step_id:
            return step
    return None


def _build_step_info(step: dict) -> Dict:
    """Build step info dictionary."""
    return {
        "id": step["id"],
        "name": STEP_NAMES.get(step["id"], step["name"]),
        "description": STEP_DESCRIPTIONS.get(
            step["id"], 
            step["description"]
        ),
        "function": step["function"]
    }


def _validate_step_id(step_id: str) -> Tuple[bool, Any]:
    """Validate step_id and return (success, target_step_num/error)."""
    try:
        return True, int(step_id)
    except ValueError:
        return False, f"معرف خطوة غير صالح: {step_id}"

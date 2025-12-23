"""Pipeline step information helpers."""

from typing import Dict, Optional, List
from src.app.pipeline.steps import AVAILABLE_STEPS
from src.app.gui.utils.translations import STEP_NAMES, STEP_DESCRIPTIONS

def get_all_steps() -> List[Dict]:
    """Get all available pipeline steps with translations."""
    steps = []
    
    for step in AVAILABLE_STEPS:
        steps.append({
            "id": step.id,
            "name": STEP_NAMES.get(step.id, step.name),
            "description": STEP_DESCRIPTIONS.get(
                step.id, 
                step.description
            )
        })
        
    return steps


def get_step_info(step_id: str) -> Optional[Dict]:
    """Get information for a specific step."""
    for step in AVAILABLE_STEPS:
        if step.id == step_id:
            return _build_step_info(step)
    return None


def _build_step_info(step: Any) -> Dict:
    """Build step info dictionary."""
    return {
        "id": step.id,
        "name": STEP_NAMES.get(step.id, step.name),
        "description": STEP_DESCRIPTIONS.get(
            step.id, 
            step.description
        ),
        "function": step.function
    }

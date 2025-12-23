"""Step lookup and validation."""

from typing import Optional
from src.app.pipeline.steps import AVAILABLE_STEPS


def find_step_by_id(step_id: str) -> Optional[dict]:
    """Find a step by its ID."""
    return next(
        (step for step in AVAILABLE_STEPS if step['id'] == step_id), None
    )


def get_steps_up_to(step_id: str) -> list:
    """Get all steps up to and including the target step ID."""
    try:
        target_step_number = int(step_id)
    except ValueError:
        return []
    
    return [
        step for step in AVAILABLE_STEPS 
        if int(step['id']) <= target_step_number
    ]


def validate_step_function(step: dict) -> bool:
    """Check if step has a valid callable function."""
    return callable(step.get('function'))

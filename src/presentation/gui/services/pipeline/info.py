"""Pipeline step information helpers."""

from typing import Dict, Optional, List, Any
from src.application.pipeline.steps import AVAILABLE_STEPS
from src.presentation.gui.utils.translations import STEP_NAMES, STEP_DESCRIPTIONS

from src.domain.models.step import Step

def get_all_steps() -> List[Step]:
    """Get all available pipeline steps with translations."""
    steps = []
    
    for step in AVAILABLE_STEPS:
        steps.append(Step(
            id=step.id,
            name=STEP_NAMES.get(step.id, step.name),
            description=STEP_DESCRIPTIONS.get(
                step.id, 
                step.description
            ),
            function=step.function
        ))
        
    return steps


def get_step_info(step_id: str) -> Optional[Step]:
    """Get information for a specific step."""
    for step in AVAILABLE_STEPS:
        if step.id == step_id:
            return _build_step_info(step)
    return None


def _build_step_info(step: Any) -> Step:
    """Build step info object."""
    return Step(
        id=step.id,
        name=STEP_NAMES.get(step.id, step.name),
        description=STEP_DESCRIPTIONS.get(
            step.id, 
            step.description
        ),
        function=step.function
    )

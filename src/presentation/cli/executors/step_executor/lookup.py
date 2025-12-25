"""Step lookup and validation (Deprecated: Use StepOrchestrator)."""

from typing import Optional, Any
from src.application.pipeline.step_orchestrator import StepOrchestrator


def find_step_by_id(step_id: str) -> Optional[Any]:
    """Find a step by its ID."""
    return StepOrchestrator.find_step(step_id)


def get_steps_up_to(step_id: str) -> list:
    """Get all steps up to and including the target step ID."""
    return StepOrchestrator.get_sequence_up_to(step_id)


def get_step_prior_to_step(target_step_id: str):
    """Get the step immediately preceding the target step."""
    return StepOrchestrator.get_previous_step(target_step_id)


def validate_step_function(step: Any) -> bool:
    """Check if step has a valid callable function."""
    if not hasattr(step, 'function'):
        return False
    return callable(step.function)

"""Pipeline step sequencing logic using centralized orchestrator."""

from typing import Tuple, Any
from src.application.pipeline.step_orchestrator import StepOrchestrator

def get_steps_sequence(step_id: str) -> Tuple[bool, Any]:
    """Get sequence of steps up to target step_id."""
    target_step_id = str(step_id) if step_id else ""
    
    steps = StepOrchestrator.get_sequence_up_to(target_step_id)
    
    if not steps:
        return False, f"لم يتم العثور على الخطوة أو التسلسل للخطوة {step_id}"
        
    return True, steps

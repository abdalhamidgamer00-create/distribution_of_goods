"""Application service for orchestrating pipeline step sequences."""

from typing import List, Optional
from src.application.pipeline.steps import AVAILABLE_STEPS
from src.domain.models.step import Step


class StepOrchestrator:
    """
    Centralizes the logic for determining which steps should be executed.
    Enforces business policies like mandatory archiving.
    """

    @staticmethod
    def get_isolated_sequence(step_id: str) -> List[Step]:
        """
        Returns a sequence containing Step 1 (Archiving) and the target step.
        If the target is Step 1, only Step 1 is returned.
        
        Args:
            step_id: The ID of the primary step to execute.
            
        Returns:
            List[Step]: The ordered list of steps to perform.
        """
        target_step = StepOrchestrator.find_step(step_id)
        if not target_step:
            return []

        # Policy: Always run Step 1 before any other step
        if step_id == "1":
            return [target_step]

        archive_step = StepOrchestrator.find_step("1")
        if not archive_step:
            return [target_step]

        return [archive_step, target_step]

    @staticmethod
    def find_step(step_id: str) -> Optional[Step]:
        """Helper to find a step by its ID."""
        for step in AVAILABLE_STEPS:
            if step.id == step_id:
                return step
        return None

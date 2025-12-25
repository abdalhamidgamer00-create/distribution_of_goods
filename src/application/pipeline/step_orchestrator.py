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
    def get_sequence_up_to(step_id: str) -> List[Step]:
        """
        Returns all steps from the beginning up to and including the target step.
        
        Args:
            step_id: The ID of the final step in the sequence.
            
        Returns:
            List[Step]: Ordered list of steps.
        """
        try:
            target_step_number = int(step_id)
        except ValueError:
            return []
            
        return [
            step for step in AVAILABLE_STEPS 
            if int(step.id) <= target_step_number
        ]

    @staticmethod
    def get_previous_step(step_id: str) -> Optional[Step]:
        """
        Returns the step immediately preceding the target step.
        
        Args:
            step_id: The ID of the target step.
            
        Returns:
            Optional[Step]: The preceding step if it exists.
        """
        sorted_steps = sorted(
            AVAILABLE_STEPS, 
            key=lambda x: int(x.id)
        )
        
        for i, step in enumerate(sorted_steps):
            if step.id == step_id:
                if i > 0:
                    return sorted_steps[i-1]
                return None
        return None

    @staticmethod
    def find_step(step_id: str) -> Optional[Step]:
        """Helper to find a step by its ID."""
        for step in AVAILABLE_STEPS:
            if step.id == step_id:
                return step
        return None

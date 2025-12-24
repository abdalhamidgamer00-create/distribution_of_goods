"""Domain models for pipeline orchestration and state tracking."""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass(frozen=True)
class PipelineContract:
    """Defines the expected output and metadata for a pipeline step."""
    service_name: str
    output_path: str
    output_type: str  # 'csv', 'excel', 'any'
    description: str


@dataclass(frozen=True)
class StepResult:
    """Captures the outcome of a single pipeline step execution."""
    service_name: str
    is_success: bool
    timestamp: datetime
    message: str
    metadata: Optional[Dict] = None


@dataclass(frozen=True)
class PipelineState:
    """Represents the overall readiness and health of the workflow."""
    step_results: Dict[str, StepResult]
    active_service: Optional[str] = None

    def is_step_ready(self, service_name: str, dependencies: List[str]) -> bool:
        """Checks if a step is ready based on its dependencies."""
        for dep in dependencies:
            if dep not in self.step_results:
                return False
            if not self.step_results[dep].is_success:
                return False
        return True

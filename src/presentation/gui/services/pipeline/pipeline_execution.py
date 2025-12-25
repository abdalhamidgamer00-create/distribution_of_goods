"""Pipeline step execution logic for the GUI."""

from typing import Tuple, Any
from src.application.pipeline.steps import AVAILABLE_STEPS
from src.presentation.gui.utils.translations import STEP_NAMES, MESSAGES
from src.shared.config.paths import (
    RENAMED_CSV_DIR, ANALYTICS_DIR, SURPLUS_DIR, 
    SHORTAGE_DIR, TRANSFERS_CSV_DIR
)


from src.domain.exceptions.pipeline_exceptions import (
    PipelineError, PrerequisiteNotFoundError, ContractViolationError
)


def run_single_step(step_id: str) -> Tuple[bool, str]:
    """Execute a single step and return status and message."""
    step = _find_step_by_id(step_id)
    if not step:
        return False, f"أداة غير موجودة: {step_id}"
    
    step_name = STEP_NAMES.get(step_id, step.name)
    try:
        # Execute the step with standard parameters
        result = step.function(use_latest_file=True)
        status_key = 'success' if result else 'failed'
        return result, f"{MESSAGES[status_key]}: {step_name}"
        
    except PrerequisiteNotFoundError as error:
        return False, MESSAGES['prerequisite_missing'].format(
            prerequisite=error.missing_prerequisite, service=error.service_name
        )
    except ContractViolationError as error:
        return False, MESSAGES['contract_violation'].format(
            service=error.service_name, detail=str(error)
        )
    except Exception as error:
        return False, f"{MESSAGES['error']} في {step_name}: {str(error)}"


def get_repository() -> Any:
    """Get a pre-configured repository instance for the GUI."""
    from src.application.factories.repository_factory import RepositoryFactory
    return RepositoryFactory.create_pandas_repository()


def _find_step_by_id(step_id: str) -> Any:
    """Helper to find a step by its integer ID string."""
    from src.application.pipeline.step_orchestrator import StepOrchestrator
    return StepOrchestrator.find_step(step_id)

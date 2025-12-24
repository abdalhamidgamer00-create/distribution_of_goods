"""Domain-specific exceptions for the distribution pipeline."""

class PipelineError(Exception):
    """Base class for all pipeline-related errors."""
    def __init__(self, message: str, service_name: str = None):
        super().__init__(message)
        self.service_name = service_name


class PrerequisiteNotFoundError(PipelineError):
    """Raised when a required prerequisite for a service is missing."""
    def __init__(self, service_name: str, missing_prerequisite: str):
        message = (
            f"Prerequisite '{missing_prerequisite}' "
            f"missing for '{service_name}'"
        )
        super().__init__(message, service_name)
        self.missing_prerequisite = missing_prerequisite


class ContractViolationError(PipelineError):
    """Raised when a service output does not meet its defined contract."""
    def __init__(self, service_name: str, detail: str):
        message = f"Contract violation for service '{service_name}': {detail}"
        super().__init__(message, service_name)


class ServiceExecutionError(PipelineError):
    """Raised when a service fails during its internal execution."""
    pass

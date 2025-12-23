"""Domain-specific exceptions."""

class DomainError(Exception):
    """Base class for all domain-related errors."""
    pass


class ValidationError(DomainError):
    """Raised when data validation fails."""
    pass


class BusinessRuleViolation(DomainError):
    """Raised when a business rule is violated."""
    pass


class ResourceNotFoundError(DomainError):
    """Raised when a required resource (e.g., product, branch) is not found."""
    pass

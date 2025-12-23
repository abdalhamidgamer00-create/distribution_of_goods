"""Allocation Calculator Package Facade."""

from src.core.domain.calculations.allocation_calculator.orchestrator import (
    calculate_proportional_allocations_vectorized,
)

__all__ = ['calculate_proportional_allocations_vectorized']

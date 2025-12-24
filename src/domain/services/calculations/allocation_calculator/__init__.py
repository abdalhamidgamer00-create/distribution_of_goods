"""Allocation Calculator Package Facade."""

from .allocation_orchestrator import (
    calculate_proportional_allocations_vectorized,
)

__all__ = ['calculate_proportional_allocations_vectorized']

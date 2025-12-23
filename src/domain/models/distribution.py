"""Domain models for distribution outcomes."""

from dataclasses import dataclass
from typing import List, Dict
from src.domain.models.entities import Product, Branch


@dataclass(frozen=True)
class Transfer:
    """Represents a movement of goods between branches."""
    product: Product
    from_branch: Branch
    to_branch: Branch
    quantity: int


@dataclass
class DistributionResult:
    """Captures the outcome of a distribution run for a product."""
    product: Product
    transfers: List[Transfer]
    remaining_needed: int
    remaining_surplus: int
    remaining_branch_surplus: Dict[str, int]
    branch_balances: Dict[str, float] = None
    total_sales: float = 0.0

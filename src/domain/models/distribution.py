"""Domain models for distribution outcomes."""

from dataclasses import dataclass
from typing import List, Dict, Optional
from src.domain.models.entities import Product, Branch


@dataclass(frozen=True)
class Transfer:
    """Represents a movement of goods between branches."""
    product: Product
    from_branch: Branch
    to_branch: Branch
    quantity: int
    sender_balance: float = 0.0
    receiver_balance: float = 0.0


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


@dataclass(frozen=True)
class LogisticsRecord:
    """Represents a single entry in a logistics report."""
    product: Product
    quantity: int
    target_branch: str
    transfer_type: str  # 'normal' or 'surplus'
    sender_balance: float
    receiver_balance: float
    category: Optional[str] = None


@dataclass(frozen=True)
class ConsolidatedLogisticsReport:
    """Encapsulates a collection of logistics records for a source branch."""
    source_branch: Branch
    records: List[LogisticsRecord]

    def has_records(self) -> bool:
        """Checks if the report contains any records."""
        return len(self.records) > 0

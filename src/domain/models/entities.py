"""Domain models for basic entities."""

from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass(frozen=True)
class Product:
    """Represents a pharmaceutical product."""
    code: str
    name: str
    category: Optional[str] = None


@dataclass(frozen=True)
class StockLevel:
    """Represents the stock status of a product in a branch."""
    needed: int
    surplus: int
    balance: float
    avg_sales: float
    sales: float = 0.0


@dataclass(frozen=True)
class Branch:
    """Represents a pharmacy branch."""
    name: str
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Branch name cannot be empty")


@dataclass(frozen=True)
class BranchStock:
    """Represents a product's stock status within a specific branch."""
    product: Product
    stock: StockLevel


@dataclass(frozen=True)
class ConsolidatedStock:
    """
    Represents a product's stock status across all branches before splitting.
    Maps branch names to their respective stock levels.
    """
    product: Product
    branch_stocks: Dict[str, StockLevel]


@dataclass(frozen=True)
class NetworkStockState:
    """
    Encapsulates the stock balances across the entire branch network.
    Structure: {branch_name: {product_code: balance}}
    """
    balances: Dict[str, Dict[str, float]]

    def get_balance(self, branch_name: str, product_code: str) -> float:
        """Retrieves balance for a specific branch and product."""
        return self.balances.get(branch_name, {}).get(product_code, 0.0)


@dataclass(frozen=True)
class SurplusEntry:
    """Represents a product with surplus stock in a branch."""
    product: Product
    quantity: int
    branch: Branch

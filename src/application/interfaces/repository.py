"""Interfaces for data persistence."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from src.domain.models.entities import (
    Product, Branch, StockLevel, ConsolidatedStock, BranchStock
)
from src.domain.models.distribution import Transfer, DistributionResult


class DataRepository(ABC):
    """Abstract interface for loading and saving domain data."""

    @abstractmethod
    def load_consolidated_stock(self) -> List[ConsolidatedStock]:
        """Load unified stock data from all branches."""
        pass

    @abstractmethod
    def save_branch_stocks(self, branch: Branch, stocks: List[BranchStock]) -> None:
        """Save stock data for a specific branch."""
        pass

    @abstractmethod
    def load_branches(self) -> List[Branch]:
        """Load all available pharmaceutical branches."""
        pass

    @abstractmethod
    def load_products(self) -> List[Product]:
        """Load all products to be processed."""
        pass

    @abstractmethod
    def load_stock_levels(self, branch: Branch) -> Dict[str, StockLevel]:
        """Load stock levels (needed, surplus, etc.) for a specific branch."""
        pass

    @abstractmethod
    def save_transfers(self, transfers: List[Transfer]) -> None:
        """Persist generated transfers."""
        pass
    @abstractmethod
    def save_remaining_surplus(self, results: List[DistributionResult]) -> None:
        """Save products with remaining surplus after distribution."""
        pass
    @abstractmethod
    def save_shortage_report(self, results: List[DistributionResult]) -> None:
        """Save products where total needed exceeds total surplus."""
        pass

    @abstractmethod
    def load_transfers(self) -> List[Transfer]:
        """Load transfers from storage."""
        pass

    @abstractmethod
    def save_split_transfers(self, transfers: List[Transfer], excel_dir: str) -> None:
        """Save transfers split by category into CSV and Excel."""
        pass

    @abstractmethod
    def load_remaining_surplus(self, branch: Branch) -> List[Dict]:
        """Load remaining surplus for a branch."""
        pass

    @abstractmethod
    def save_combined_transfers(
        self, 
        branch: Branch,
        merged_data: List[Dict], 
        separate_data: List[Dict],
        timestamp: str
    ) -> None:
        """Save combined transfers (merged and separate) with formatting."""
        pass

    @abstractmethod
    def list_outputs(self, category: str, branch_name: Optional[str] = None) -> List[Dict]:
        """Lists available output artifacts for a given category and optional branch."""
        pass

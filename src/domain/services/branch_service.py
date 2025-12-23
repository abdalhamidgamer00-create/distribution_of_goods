"""Domain service for branch data splitting."""

from typing import List, Dict
from src.domain.models.entities import (
    Branch, BranchStock, ConsolidatedStock
)


class BranchSplitter:
    """Logic for extracting branch-specific data from consolidated records."""

    @staticmethod
    def split_by_branch(
        consolidated_data: List[ConsolidatedStock],
        branches: List[Branch]
    ) -> Dict[str, List[BranchStock]]:
        """
        Groups stock data by branch name.
        Returns a dictionary mapping branch name to its list of stocks.
        """
        results = {branch.name: [] for branch in branches}

        for record in consolidated_data:
            for branch_name, stock in record.branch_stocks.items():
                if branch_name in results:
                    results[branch_name].append(
                        BranchStock(product=record.product, stock=stock)
                    )
        
        return results

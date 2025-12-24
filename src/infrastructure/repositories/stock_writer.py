"""Specialized component for persisting stock data to disk."""

import os
from typing import List
from src.domain.models.entities import Branch, BranchStock
from src.infrastructure.repositories.mappers import StockMapper


class StockWriter:
    """Handles persistence of branch-specific stock information."""

    def __init__(self, analytics_directory: str):
        self._analytics_directory = analytics_directory

    def save_branch_stocks(
        self, branch: Branch, stocks: List[BranchStock]
    ) -> None:
        """Saves branch stock levels to a standardized CSV format."""
        dataframe = StockMapper.to_branch_dataframe(stocks)
        directory = os.path.join(self._analytics_directory, branch.name)
        os.makedirs(directory, exist_ok=True)
        filename = f"main_analysis_{branch.name}.csv"
        path = os.path.join(directory, filename)
        dataframe.to_csv(path, index=False, encoding='utf-8-sig')

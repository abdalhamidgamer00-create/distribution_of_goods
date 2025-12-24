"""Service for creating domain models from raw repository data."""

from typing import List, Dict
from src.domain.models.entities import (
    Product, Branch, NetworkStockState, SurplusEntry
)


class DomainModelFactory:
    """Encapsulates the creation of complex domain entity structures."""

    @staticmethod
    def create_network_state(
        branches: List[Branch], 
        repository_loader_function
    ) -> NetworkStockState:
        """Creates a NetworkStockState snapshot from the repository."""
        balances_map = {}
        for branch in branches:
            stocks = repository_loader_function(branch)
            balances_map[branch.name] = {
                code: stock.balance for code, stock in stocks.items()
            }
        return NetworkStockState(balances=balances_map)

    @staticmethod
    def create_surplus_entries(
        raw_surplus_list: List[Dict], 
        branch: Branch
    ) -> List[SurplusEntry]:
        """Converts raw surplus dictionaries into SurplusEntry entities."""
        entries = []
        for raw in raw_surplus_list:
            product = Product(code=raw['code'], name=raw['product_name'])
            entries.append(SurplusEntry(
                product=product,
                quantity=raw['quantity'],
                branch=branch
            ))
        return entries

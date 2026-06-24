"""Tests for domain.services.model_factory module."""

import pytest
from unittest.mock import MagicMock

from src.domain.models.entities import (
    Product, Branch, StockLevel, NetworkStockState, SurplusEntry,
)
from src.domain.services.model_factory import DomainModelFactory


def _stock(needed=0, surplus=0, balance=10.0, avg_sales=1.0):
    return StockLevel(
        needed=needed, surplus=surplus, balance=balance,
        average_daily_sales=avg_sales,
    )


class TestCreateNetworkState:
    def test_basic_network_state(self):
        branches = [Branch(name="admin"), Branch(name="star")]

        def loader(branch, config=None):
            if branch.name == "admin":
                return {"001": _stock(balance=10.0), "002": _stock(balance=5.0)}
            return {"001": _stock(balance=20.0)}

        state = DomainModelFactory.create_network_state(branches, loader)
        assert isinstance(state, NetworkStockState)
        assert state.get_balance("admin", "001") == 10.0
        assert state.get_balance("admin", "002") == 5.0
        assert state.get_balance("star", "001") == 20.0

    def test_empty_branches(self):
        state = DomainModelFactory.create_network_state([], lambda b, config=None: {})
        assert state.balances == {}

    def test_passes_config_to_loader(self):
        loader = MagicMock(return_value={})
        branches = [Branch(name="admin")]
        config = {"coverage_days": 30}
        DomainModelFactory.create_network_state(branches, loader, config)
        loader.assert_called_once_with(branches[0], config=config)


class TestCreateSurplusEntries:
    def test_basic_conversion(self):
        branch = Branch(name="admin")
        raw_list = [
            {'code': '001', 'product_name': 'Aspirin Tab', 'quantity': 10},
            {'code': '002', 'product_name': 'Cough Syrup', 'quantity': 5},
        ]
        entries = DomainModelFactory.create_surplus_entries(raw_list, branch)
        assert len(entries) == 2
        assert all(isinstance(e, SurplusEntry) for e in entries)
        assert entries[0].product.code == '001'
        assert entries[0].quantity == 10
        assert entries[0].branch == branch

    def test_empty_list(self):
        branch = Branch(name="admin")
        entries = DomainModelFactory.create_surplus_entries([], branch)
        assert entries == []

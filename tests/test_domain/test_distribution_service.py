"""Tests for domain.services.distribution_service module."""

import pytest

from src.domain.models.entities import Product, Branch, StockLevel
from src.domain.models.distribution import Transfer, DistributionResult
from src.domain.services.distribution_service import DistributionEngine
from src.domain.services.priority_service import PriorityCalculator


def _stock(needed=0, surplus=0, balance=10.0, avg_sales=1.0, shortage=0):
    return StockLevel(
        needed=needed, surplus=surplus, balance=balance,
        average_daily_sales=avg_sales, shortage=shortage,
    )


class TestDistributionEngine:
    def setup_method(self):
        self.engine = DistributionEngine(PriorityCalculator())

    def test_basic_distribution(self):
        product = Product(code="001", name="Aspirin Tab")
        needing = [
            (Branch(name="star"), _stock(needed=3, balance=2.0, avg_sales=0.5)),
        ]
        surplus = [
            (Branch(name="admin"), _stock(surplus=5, balance=20.0, avg_sales=1.0)),
        ]
        result = self.engine.distribute_product(product, needing, surplus)
        assert isinstance(result, DistributionResult)
        assert len(result.transfers) >= 1
        total_transferred = sum(t.quantity for t in result.transfers)
        assert total_transferred == 3

    def test_no_surplus_no_transfers(self):
        product = Product(code="001", name="Aspirin Tab")
        needing = [
            (Branch(name="star"), _stock(needed=3, balance=2.0, avg_sales=0.5)),
        ]
        surplus = [
            (Branch(name="admin"), _stock(surplus=0, balance=20.0, avg_sales=1.0)),
        ]
        result = self.engine.distribute_product(product, needing, surplus)
        assert len(result.transfers) == 0
        assert result.remaining_needed == 3

    def test_partial_distribution(self):
        product = Product(code="001", name="Aspirin Tab")
        needing = [
            (Branch(name="star"), _stock(needed=10, balance=2.0, avg_sales=0.5)),
        ]
        surplus = [
            (Branch(name="admin"), _stock(surplus=3, balance=20.0, avg_sales=1.0)),
        ]
        result = self.engine.distribute_product(product, needing, surplus)
        total_transferred = sum(t.quantity for t in result.transfers)
        assert total_transferred == 3
        assert result.remaining_needed == 7

    def test_multiple_needing_branches(self):
        product = Product(code="001", name="Aspirin Tab")
        needing = [
            (Branch(name="star"), _stock(needed=3, balance=2.0, avg_sales=0.5)),
            (Branch(name="shahid"), _stock(needed=2, balance=1.0, avg_sales=0.8)),
        ]
        surplus = [
            (Branch(name="admin"), _stock(surplus=10, balance=20.0, avg_sales=1.0)),
        ]
        result = self.engine.distribute_product(product, needing, surplus)
        total_transferred = sum(t.quantity for t in result.transfers)
        assert total_transferred == 5

    def test_multiple_surplus_branches(self):
        product = Product(code="001", name="Aspirin Tab")
        needing = [
            (Branch(name="star"), _stock(needed=5, balance=2.0, avg_sales=0.5)),
        ]
        surplus = [
            (Branch(name="admin"), _stock(surplus=3, balance=20.0, avg_sales=1.0)),
            (Branch(name="wardani"), _stock(surplus=4, balance=15.0, avg_sales=0.8)),
        ]
        result = self.engine.distribute_product(product, needing, surplus)
        total_transferred = sum(t.quantity for t in result.transfers)
        assert total_transferred == 5

    def test_empty_needing_branches(self):
        product = Product(code="001", name="Aspirin Tab")
        needing = []
        surplus = [
            (Branch(name="admin"), _stock(surplus=5, balance=20.0, avg_sales=1.0)),
        ]
        result = self.engine.distribute_product(product, needing, surplus)
        assert len(result.transfers) == 0

    def test_transfer_has_correct_balances(self):
        product = Product(code="001", name="Aspirin Tab")
        needing = [
            (Branch(name="star"), _stock(needed=1, balance=2.0, avg_sales=0.5)),
        ]
        surplus = [
            (Branch(name="admin"), _stock(surplus=5, balance=20.0, avg_sales=1.0)),
        ]
        result = self.engine.distribute_product(product, needing, surplus)
        transfer = result.transfers[0]
        assert transfer.sender_balance == 20.0
        assert transfer.receiver_balance == 2.0

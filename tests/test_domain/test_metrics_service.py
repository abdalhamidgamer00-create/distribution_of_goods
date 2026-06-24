"""Tests for domain.services.distribution.metrics_service module."""

import pytest

from src.domain.models.entities import Product, Branch, StockLevel
from src.domain.models.distribution import Transfer, DistributionResult
from src.domain.services.distribution.metrics_service import DistributionMetricsService


def _stock(needed=0, surplus=0, balance=10.0, avg_sales=1.0, shortage=0):
    return StockLevel(
        needed=needed, surplus=surplus, balance=balance,
        average_daily_sales=avg_sales, shortage=shortage,
    )


def _transfer(from_name="admin", to_name="star", qty=5):
    return Transfer(
        product=Product(code="001", name="Aspirin Tab"),
        from_branch=Branch(name=from_name),
        to_branch=Branch(name=to_name),
        quantity=qty,
        sender_balance=20.0,
        receiver_balance=5.0,
    )


class TestDistributionMetricsService:
    def test_build_result_basic(self):
        product = Product(code="001", name="Aspirin Tab")
        transfers = [_transfer("admin", "star", 3)]
        original_needs = [
            (Branch(name="star"), _stock(needed=5, shortage=10)),
        ]
        surplus = {"admin": 2}

        result = DistributionMetricsService.build_result(
            product, transfers, original_needs, surplus
        )
        assert isinstance(result, DistributionResult)
        assert result.remaining_needed == 2  # 5 - 3
        assert result.remaining_surplus == 2

    def test_fully_fulfilled(self):
        product = Product(code="001", name="Aspirin Tab")
        transfers = [_transfer("admin", "star", 5)]
        original_needs = [
            (Branch(name="star"), _stock(needed=5, shortage=5)),
        ]
        surplus = {"admin": 0}

        result = DistributionMetricsService.build_result(
            product, transfers, original_needs, surplus
        )
        assert result.remaining_needed == 0
        assert result.remaining_shortage == 0

    def test_no_transfers(self):
        product = Product(code="001", name="Aspirin Tab")
        original_needs = [
            (Branch(name="star"), _stock(needed=5, shortage=10)),
        ]
        surplus = {"admin": 3}

        result = DistributionMetricsService.build_result(
            product, [], original_needs, surplus
        )
        assert result.remaining_needed == 5
        assert result.remaining_shortage == max(0, 10 - 3)

    def test_multiple_needing_branches(self):
        product = Product(code="001", name="Aspirin Tab")
        transfers = [
            _transfer("admin", "star", 2),
            _transfer("admin", "shahid", 3),
        ]
        original_needs = [
            (Branch(name="star"), _stock(needed=5, shortage=8)),
            (Branch(name="shahid"), _stock(needed=4, shortage=6)),
        ]
        surplus = {"admin": 0}

        result = DistributionMetricsService.build_result(
            product, transfers, original_needs, surplus
        )
        assert result.remaining_needed == (5 - 2) + (4 - 3)  # 3 + 1 = 4

    def test_remaining_branch_surplus(self):
        product = Product(code="001", name="Aspirin Tab")
        transfers = [_transfer("admin", "star", 3)]
        original_needs = [
            (Branch(name="star"), _stock(needed=5)),
        ]
        surplus = {"admin": 7, "wardani": 3}

        result = DistributionMetricsService.build_result(
            product, transfers, original_needs, surplus
        )
        assert result.remaining_branch_surplus == {"admin": 7, "wardani": 3}
        assert result.remaining_surplus == 10

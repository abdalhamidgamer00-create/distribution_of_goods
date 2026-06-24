"""Tests for domain.services.branch_service module."""

import pytest

from src.domain.models.entities import (
    Product, Branch, StockLevel, BranchStock, ConsolidatedStock,
)
from src.domain.services.branch_service import BranchSplitter


def _stock(needed=0, surplus=0, balance=10.0, avg_sales=1.0):
    return StockLevel(
        needed=needed, surplus=surplus, balance=balance,
        average_daily_sales=avg_sales,
    )


class TestBranchSplitter:
    def test_split_single_product_multiple_branches(self):
        branches = [Branch(name="admin"), Branch(name="star")]
        product = Product(code="001", name="Aspirin Tab")
        consolidated = [
            ConsolidatedStock(
                product=product,
                branch_stocks={
                    "admin": _stock(needed=5, balance=10.0),
                    "star": _stock(surplus=3, balance=20.0),
                }
            )
        ]
        result = BranchSplitter.split_by_branch(consolidated, branches)
        assert len(result["admin"]) == 1
        assert len(result["star"]) == 1
        assert result["admin"][0].product == product
        assert result["admin"][0].stock.needed == 5

    def test_split_multiple_products(self):
        branches = [Branch(name="admin")]
        p1 = Product(code="001", name="Aspirin Tab")
        p2 = Product(code="002", name="Cough Syrup")
        consolidated = [
            ConsolidatedStock(
                product=p1,
                branch_stocks={"admin": _stock(needed=5)},
            ),
            ConsolidatedStock(
                product=p2,
                branch_stocks={"admin": _stock(surplus=3)},
            ),
        ]
        result = BranchSplitter.split_by_branch(consolidated, branches)
        assert len(result["admin"]) == 2

    def test_branch_not_in_consolidated_gets_empty_list(self):
        branches = [Branch(name="admin"), Branch(name="star")]
        product = Product(code="001", name="Aspirin Tab")
        consolidated = [
            ConsolidatedStock(
                product=product,
                branch_stocks={"admin": _stock(needed=5)},
            ),
        ]
        result = BranchSplitter.split_by_branch(consolidated, branches)
        assert result["star"] == []

    def test_empty_consolidated_returns_empty_lists(self):
        branches = [Branch(name="admin"), Branch(name="star")]
        result = BranchSplitter.split_by_branch([], branches)
        assert result == {"admin": [], "star": []}

"""Tests for domain.services.priority_service module."""

import pytest

from src.domain.models.entities import StockLevel
from src.domain.services.priority_service import PriorityCalculator


def _stock(needed=0, surplus=0, balance=10.0, avg_sales=1.0, shortage=0):
    return StockLevel(
        needed=needed, surplus=surplus, balance=balance,
        average_daily_sales=avg_sales, shortage=shortage,
    )


class TestCalculateVulnerabilityScore:
    def test_zero_needed_returns_zero(self):
        stock = _stock(needed=0, balance=50.0, avg_sales=2.0)
        score = PriorityCalculator.calculate_vulnerability_score(stock)
        assert score == 0.0

    def test_negative_needed_returns_zero(self):
        stock = _stock(needed=-5, balance=50.0, avg_sales=2.0)
        score = PriorityCalculator.calculate_vulnerability_score(stock)
        assert score == 0.0

    def test_high_needed_high_score(self):
        low_need = _stock(needed=2, balance=10.0, avg_sales=1.0)
        high_need = _stock(needed=20, balance=10.0, avg_sales=1.0)
        low_score = PriorityCalculator.calculate_vulnerability_score(low_need)
        high_score = PriorityCalculator.calculate_vulnerability_score(high_need)
        assert high_score > low_score

    def test_low_balance_high_score(self):
        high_bal = _stock(needed=5, balance=50.0, avg_sales=1.0)
        low_bal = _stock(needed=5, balance=1.0, avg_sales=1.0)
        high_bal_score = PriorityCalculator.calculate_vulnerability_score(high_bal)
        low_bal_score = PriorityCalculator.calculate_vulnerability_score(low_bal)
        assert low_bal_score > high_bal_score

    def test_zero_balance_no_division_error(self):
        stock = _stock(needed=5, balance=0.0, avg_sales=1.0)
        score = PriorityCalculator.calculate_vulnerability_score(stock)
        assert score > 0.0

    def test_high_avg_sales_increases_score(self):
        low_sales = _stock(needed=5, balance=10.0, avg_sales=0.1)
        high_sales = _stock(needed=5, balance=10.0, avg_sales=5.0)
        low_score = PriorityCalculator.calculate_vulnerability_score(low_sales)
        high_score = PriorityCalculator.calculate_vulnerability_score(high_sales)
        assert high_score > low_score


class TestCalculateSurplusRank:
    def test_returns_surplus_value(self):
        stock = _stock(surplus=15)
        rank = PriorityCalculator.calculate_surplus_rank(stock)
        assert rank == 15

    def test_zero_surplus(self):
        stock = _stock(surplus=0)
        rank = PriorityCalculator.calculate_surplus_rank(stock)
        assert rank == 0

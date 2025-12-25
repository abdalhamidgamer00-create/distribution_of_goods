"""Unit tests for the centralized InventoryPolicy."""

import pytest
import pandas as pd
from src.domain.services.inventory.inventory_policy import InventoryPolicy
from src.shared.constants import (
    MAX_BALANCE_FOR_NEED_THRESHOLD,
    MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION,
    MIN_NEED_THRESHOLD
)


class TestInventoryPolicyScalar:
    """Tests for apply_scalar_rules method."""

    def test_max_balance_suppression(self):
        """Should zero out need if balance >= threshold."""
        # Threshold is 30
        result = InventoryPolicy.apply_scalar_rules(
            needed=10, 
            balance=MAX_BALANCE_FOR_NEED_THRESHOLD, 
            coverage=20
        )
        assert result == 0

    def test_small_need_suppression(self):
        """Should zero out small needs for high coverage products."""
        # Coverage >= 15 and need < 10
        result = InventoryPolicy.apply_scalar_rules(
            needed=5, 
            balance=10, 
            coverage=MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION
        )
        assert result == 0

    def test_small_need_not_suppressed_low_coverage(self):
        """Should NOT zero out small needs if coverage is low."""
        result = InventoryPolicy.apply_scalar_rules(
            needed=5, 
            balance=10, 
            coverage=MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION - 1
        )
        assert result == 5

    def test_max_balance_capping(self):
        """Should cap need so total doesn't exceed 30."""
        # Balance 25, need 10 -> total 35 -> capped need 5
        result = InventoryPolicy.apply_scalar_rules(
            needed=10, 
            balance=25, 
            coverage=20
        )
        assert result == 5


class TestInventoryPolicyVectorized:
    """Tests for apply_vectorized_rules method."""

    def test_vectorized_application(self):
        """Should apply all rules correctly to a DataFrame."""
        df = pd.DataFrame({
            'balance': [30.0, 10.0, 25.0, 10.0],
            'coverage_quantity': [20, 15, 20, 5],
            'needed_quantity': [10, 5, 10, 5]
        })
        
        result_df = InventoryPolicy.apply_vectorized_rules(df)
        
        # Row 0: Max Balance (30) -> 0
        assert result_df.iloc[0]['needed_quantity'] == 0
        # Row 1: Small Need (Coverage 15, Need 5) -> 0
        assert result_df.iloc[1]['needed_quantity'] == 0
        # Row 2: Capping (Balance 25, Need 10) -> 5
        assert result_df.iloc[2]['needed_quantity'] == 5
        # Row 3: No suppression (Coverage 5, Need 5) -> 5
        assert result_df.iloc[3]['needed_quantity'] == 5

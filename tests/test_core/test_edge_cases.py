"""Edge case tests for src/core to achieve 100% coverage.

These tests target the specific uncovered lines:
- allocation_calculator.py: lines 50, 98
- data_validator.py: lines 14-15, 151, 171
"""

import math
import pandas as pd
import pytest
from datetime import datetime


# ===================== allocation_calculator Edge Cases =====================

class TestAllocationCalculatorEdgeCases:
    """Edge case tests for allocation_calculator.py."""
    
    def test_calculate_proportions_with_zero_total_scores(self):
        """
        WHAT: Test _calculate_proportions when total_scores_sum is 0
        WHY: Cover line 50 - fallback to needed-based proportions
        BREAKS: Division by zero in allocation
        """
        from src.core.domain.calculations.allocation_calculator import (
            _build_branch_matrices,
            _calculate_proportions,
        )
        
        # Create branch data where weighted scores sum to zero
        branches = ['branch1', 'branch2']
        branch_data = {
            'branch1': pd.DataFrame({
                'avg_sales': [0.0],
                'balance': [0.0],
                'needed_quantity': [10.0],
                'surplus_quantity': [0.0]
            }),
            'branch2': pd.DataFrame({
                'avg_sales': [0.0],
                'balance': [0.0],
                'needed_quantity': [10.0],
                'surplus_quantity': [0.0]
            })
        }
        
        matrices = _build_branch_matrices(branch_data, branches)
        
        # Create zero total_scores
        total_scores = pd.Series([0.0, 0.0], index=branches)
        
        # This should trigger line 50 (fallback path)
        result = _calculate_proportions(matrices, 0, total_scores, 20.0, branches)
        
        # Should return some proportions
        assert isinstance(result, pd.Series)
        assert len(result) == len(branches)
    
    def test_process_single_product_zero_needed(self):
        """
        WHAT: Test _process_single_product_allocation when total_needed <= 0
        WHY: Cover line 98 - return None for products with no need
        BREAKS: Unnecessary processing of fully-stocked products
        """
        from src.core.domain.calculations.allocation_calculator import (
            _build_branch_matrices,
            _process_single_product_allocation,
        )
        
        # Create branch data where needed_quantity is 0
        branches = ['branch1', 'branch2']
        branch_data = {
            'branch1': pd.DataFrame({
                'avg_sales': [1.0],
                'balance': [100.0],
                'needed_quantity': [0.0],  # No need
                'surplus_quantity': [50.0]
            }),
            'branch2': pd.DataFrame({
                'avg_sales': [1.0],
                'balance': [100.0],
                'needed_quantity': [0.0],  # No need
                'surplus_quantity': [50.0]
            })
        }
        
        matrices = _build_branch_matrices(branch_data, branches)
        total_surplus = pd.Series([100.0])
        total_needed = pd.Series([0.0])  # Zero total needed
        
        # This should return None (line 98)
        result = _process_single_product_allocation(
            0, matrices, total_surplus, total_needed, branches, branch_data
        )
        
        assert result is None


# ===================== data_validator Edge Cases =====================

class TestDataValidatorEdgeCases:
    """Edge case tests for data_validator.py."""
    
    def test_parse_date_strings_invalid_format(self):
        """
        WHAT: Test _parse_date_strings with invalid date format
        WHY: Cover lines 14-15 - ValueError exception handling
        BREAKS: Crash on malformed date strings
        """
        from src.core.validation.data_validator import _parse_date_strings
        
        # Invalid date format
        invalid_dates = ["not-a-date", "invalid"]
        
        result = _parse_date_strings(invalid_dates)
        
        # Should return (None, None) on ValueError
        assert result == (None, None)
    
    def test_parse_date_strings_invalid_day(self):
        """
        WHAT: Test with syntactically correct but invalid date
        WHY: Additional coverage for ValueError path
        BREAKS: Crash on invalid day number
        """
        from src.core.validation.data_validator import _parse_date_strings
        
        # Day 32 is invalid
        invalid_dates = ["32/01/2024 10:00", "01/01/2024 10:00"]
        
        result = _parse_date_strings(invalid_dates)
        
        assert result == (None, None)
    
    def test_try_validate_headers_empty_header_line(self, tmp_path):
        """
        WHAT: Test _try_validate_headers with empty header line
        WHY: Cover line 171 - empty header returns error
        BREAKS: IndexError on empty file
        """
        from src.core.validation.data_validator import validate_csv_headers
        
        # Create CSV with empty second line
        csv_file = tmp_path / "empty_header.csv"
        csv_file.write_text("01/01/2024 10:00 - 01/04/2024 10:00\n\n")
        
        is_valid, errors, message = validate_csv_headers(str(csv_file))
        
        # Should report empty header error
        assert is_valid is False
        assert "empty" in message.lower() or len(errors) > 0
    
    def test_check_optional_present_no_optional_columns(self, tmp_path):
        """
        WHAT: Test when no optional columns are present
        WHY: Cover path when optional_warning is None
        BREAKS: Incorrect warning messages
        """
        from src.core.validation.data_validator import (
            _check_optional_present,
            _get_optional_headers,
        )
        
        # Headers with no optional columns
        actual_headers = ["كود", "إسم الصنف"]
        optional_headers = _get_optional_headers()
        
        result = _check_optional_present(actual_headers, optional_headers)
        
        # Should return None when no optional columns found
        assert result is None


# ===================== Additional Boundary Tests =====================

class TestAllocationBoundaryConditions:
    """Boundary condition tests for allocation functions."""
    
    def test_allocations_with_single_branch(self):
        """
        WHAT: Test allocation with only one branch
        WHY: Edge case for single-branch scenarios
        BREAKS: Index errors with single element
        """
        from src.core.domain.calculations.allocation_calculator import (
            calculate_proportional_allocations_vectorized,
        )
        
        branches = ['single_branch']
        branch_data = {
            'single_branch': pd.DataFrame({
                'avg_sales': [1.0, 2.0],
                'balance': [10.0, 20.0],
                'needed_quantity': [5.0, 10.0],
                'surplus_quantity': [0.0, 0.0]
            })
        }
        
        # Should not crash with single branch
        result = calculate_proportional_allocations_vectorized(branch_data, branches)
        
        assert isinstance(result, dict)
    
    def test_normalize_scores_identical_values(self):
        """
        WHAT: Test _normalize_scores when all values are identical
        WHY: Edge case where max - min = 0
        BREAKS: Division by zero
        """
        from src.core.domain.calculations.allocation_calculator import _normalize_scores
        
        # All identical values
        series = pd.Series([5.0, 5.0, 5.0])
        
        result = _normalize_scores(series)
        
        # Should return all 1.0 when values are identical
        assert all(result == 1.0)


class TestValidatorBoundaryConditions:
    """Boundary condition tests for validation functions."""
    
    def test_validate_date_range_with_exact_minimum(self):
        """
        WHAT: Test date range with exactly 3 months
        WHY: Boundary condition for minimum months
        BREAKS: Off-by-one error in month calculation
        """
        from src.core.validation.data_validator import validate_date_range_months
        
        start = datetime(2024, 1, 1)
        end = datetime(2024, 4, 1)  # Exactly 3 months
        
        result = validate_date_range_months(start, end, min_months=3)
        
        assert result is True
    
    def test_calculate_days_between_same_day(self):
        """
        WHAT: Test days calculation for same day
        WHY: Minimum days should be 1
        BREAKS: Returns 0 for same day
        """
        from src.core.validation.data_validator import calculate_days_between
        
        date = datetime(2024, 1, 1)
        
        result = calculate_days_between(date, date)
        
        # Should return at least 1 day
        assert result >= 1

"""Tests for dataframe validator functions"""

import pandas as pd
import pytest

from src.shared.dataframes.validators import (
    ensure_columns,
    clean_numeric,
    clean_numeric_series,
    subset_rows
)


class TestEnsureColumns:
    """Tests for ensure_columns function"""
    
    def test_all_columns_present(self):
        """Test when all required columns are present"""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6],
            'col3': [7, 8, 9]
        })
        
        result = ensure_columns(df, ['col1', 'col2'])
        
        assert result is not None
        assert len(result) == 3
    
    def test_missing_columns_raises_error(self):
        """Test that missing columns raise ValueError"""
        df = pd.DataFrame({
            'col1': [1, 2, 3]
        })
        
        with pytest.raises(ValueError) as exc_info:
            ensure_columns(df, ['col1', 'col2', 'col3'])
        
        assert 'col2' in str(exc_info.value) or 'col3' in str(exc_info.value)
    
    def test_context_in_error_message(self):
        """Test that context appears in error message"""
        df = pd.DataFrame({'col1': [1]})
        
        with pytest.raises(ValueError) as exc_info:
            ensure_columns(df, ['col2'], context='test_context')
        
        assert 'test_context' in str(exc_info.value)
    
    def test_empty_required_list(self):
        """Test with empty required columns list"""
        df = pd.DataFrame({'col1': [1]})
        
        result = ensure_columns(df, [])
        
        assert result is not None


class TestCleanNumeric:
    """Tests for clean_numeric function"""
    
    def test_integer_input(self):
        """Test with integer input"""
        assert clean_numeric(42) == 42.0
    
    def test_float_input(self):
        """Test with float input"""
        assert clean_numeric(3.14) == 3.14
    
    def test_string_number(self):
        """Test with string number"""
        assert clean_numeric("123") == 123.0
    
    def test_string_with_commas(self):
        """Test with string containing commas"""
        assert clean_numeric("1,234") == 1234.0
        assert clean_numeric("1,234,567") == 1234567.0
    
    def test_none_input(self):
        """Test with None input"""
        assert clean_numeric(None) == 0.0
    
    def test_empty_string(self):
        """Test with empty string"""
        assert clean_numeric("") == 0.0
    
    def test_invalid_string(self):
        """Test with invalid string"""
        assert clean_numeric("abc") == 0.0
    
    def test_string_with_spaces(self):
        """Test with string containing spaces"""
        assert clean_numeric("  123  ") == 123.0
    
    def test_negative_number(self):
        """Test with negative number"""
        assert clean_numeric(-42) == -42.0
        assert clean_numeric("-42") == -42.0


class TestCleanNumericSeries:
    """Tests for clean_numeric_series function"""
    
    def test_numeric_series(self):
        """Test with numeric series"""
        series = pd.Series([1, 2, 3, 4, 5])
        
        result = clean_numeric_series(series)
        
        assert result.dtype == float
        assert list(result) == [1.0, 2.0, 3.0, 4.0, 5.0]
    
    def test_string_series(self):
        """Test with string series"""
        series = pd.Series(["1", "2", "3"])
        
        result = clean_numeric_series(series)
        
        # Should be numeric (could be int or float depending on values)
        assert pd.api.types.is_numeric_dtype(result)
        assert list(result) == [1.0, 2.0, 3.0]
    
    def test_series_with_commas(self):
        """Test with series containing commas"""
        series = pd.Series(["1,000", "2,500", "3,750"])
        
        result = clean_numeric_series(series)
        
        assert list(result) == [1000.0, 2500.0, 3750.0]
    
    def test_series_with_nan(self):
        """Test with series containing NaN"""
        series = pd.Series([1.0, None, 3.0])
        
        result = clean_numeric_series(series)
        
        assert result.iloc[1] == 0.0  # NaN should be replaced with 0
    
    def test_mixed_series(self):
        """Test with mixed types series"""
        series = pd.Series(["1", 2, "3.5"])
        
        result = clean_numeric_series(series)
        
        assert result.dtype == float


class TestSubsetRows:
    """Tests for subset_rows function"""
    
    def test_boolean_mask(self):
        """Test with boolean mask"""
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e']
        })
        
        mask = [True, False, True, False, True]
        result = subset_rows(df, mask)
        
        assert len(result) == 3
        assert list(result['col1']) == [1, 3, 5]
    
    def test_series_mask(self):
        """Test with Series mask"""
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5]
        })
        
        mask = df['col1'] > 2
        result = subset_rows(df, mask)
        
        assert len(result) == 3
        assert list(result['col1']) == [3, 4, 5]
    
    def test_returns_copy(self):
        """Test that function returns a copy, not view"""
        df = pd.DataFrame({'col1': [1, 2, 3]})
        mask = [True, True, True]
        
        result = subset_rows(df, mask)
        result['col1'] = [10, 20, 30]
        
        # Original should be unchanged
        assert list(df['col1']) == [1, 2, 3]
    
    def test_all_false_mask(self):
        """Test with all False mask"""
        df = pd.DataFrame({'col1': [1, 2, 3]})
        mask = [False, False, False]
        
        result = subset_rows(df, mask)
        
        assert len(result) == 0

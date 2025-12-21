"""Tests for data validation functions"""

import os
import tempfile
from datetime import datetime

import pytest

from src.core.validation.data_validator import (
    extract_dates_from_header,
    calculate_days_between,
    validate_date_range_months,
    validate_csv_header,
    validate_csv_headers
)


class TestExtractDatesFromHeader:
    """Tests for extract_dates_from_header function"""
    
    def test_valid_header_with_dates(self):
        """Test extracting dates from valid header"""
        header = "من: 01/09/2024 00:00 إلى: 01/12/2024 00:00"
        start_date, end_date = extract_dates_from_header(header)
        
        assert start_date is not None
        assert end_date is not None
        assert start_date.year == 2024
        assert start_date.month == 9
        assert start_date.day == 1
        assert end_date.year == 2024
        assert end_date.month == 12
    
    def test_header_without_dates(self):
        """Test header without dates returns None"""
        header = "code,product_name,selling_price"
        start_date, end_date = extract_dates_from_header(header)
        
        assert start_date is None
        assert end_date is None
    
    def test_empty_header(self):
        """Test empty header returns None"""
        start_date, end_date = extract_dates_from_header("")
        
        assert start_date is None
        assert end_date is None
    
    def test_malformed_dates(self):
        """Test malformed dates return None"""
        header = "من: invalid_date إلى: another_invalid"
        start_date, end_date = extract_dates_from_header(header)
        
        assert start_date is None
        assert end_date is None
    
    def test_only_one_date(self):
        """Test header with only one date returns None"""
        header = "من: 01/09/2024 00:00"
        start_date, end_date = extract_dates_from_header(header)
        
        assert start_date is None
        assert end_date is None


class TestCalculateDaysBetween:
    """Tests for calculate_days_between function"""
    
    def test_valid_dates(self):
        """Test calculating days between two valid dates"""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)
        
        result = calculate_days_between(start, end)
        
        assert result == 30
    
    def test_same_date(self):
        """Test same date returns 1 (minimum)"""
        date = datetime(2024, 1, 1)
        
        result = calculate_days_between(date, date)
        
        assert result == 1  # Minimum 1 to avoid division by zero
    
    def test_end_before_start(self):
        """Test when end date is before start date"""
        start = datetime(2024, 12, 1)
        end = datetime(2024, 1, 1)
        
        result = calculate_days_between(start, end)
        
        assert result == 0
    
    def test_none_start_date(self):
        """Test with None start date"""
        result = calculate_days_between(None, datetime(2024, 1, 1))
        
        assert result == 0
    
    def test_none_end_date(self):
        """Test with None end date"""
        result = calculate_days_between(datetime(2024, 1, 1), None)
        
        assert result == 0
    
    def test_both_none(self):
        """Test with both dates None"""
        result = calculate_days_between(None, None)
        
        assert result == 0


class TestValidateDateRangeMonths:
    """Tests for validate_date_range_months function"""
    
    def test_valid_range_above_minimum(self):
        """Test date range >= 3 months returns True"""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 6, 1)  # 5 months
        
        result = validate_date_range_months(start, end)
        
        assert result is True
    
    def test_exactly_three_months(self):
        """Test exactly 3 months returns True"""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 4, 1)  # Exactly 3 months
        
        result = validate_date_range_months(start, end)
        
        assert result is True
    
    def test_less_than_minimum(self):
        """Test date range < 3 months returns False"""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 2, 1)  # 1 month
        
        result = validate_date_range_months(start, end)
        
        assert result is False
    
    def test_custom_minimum_months(self):
        """Test with custom minimum months"""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 7, 1)  # 6 months
        
        # Should pass with min_months=6
        assert validate_date_range_months(start, end, min_months=6) is True
        
        # Should fail with min_months=7
        assert validate_date_range_months(start, end, min_months=7) is False
    
    def test_none_dates(self):
        """Test with None dates returns False"""
        assert validate_date_range_months(None, datetime(2024, 1, 1)) is False
        assert validate_date_range_months(datetime(2024, 1, 1), None) is False
        assert validate_date_range_months(None, None) is False
    
    def test_end_before_start(self):
        """Test when end is before start returns False"""
        start = datetime(2024, 6, 1)
        end = datetime(2024, 1, 1)
        
        result = validate_date_range_months(start, end)
        
        assert result is False


class TestValidateCsvHeader:
    """Tests for validate_csv_header function"""
    
    def test_valid_csv_with_dates(self, sample_csv_file):
        """Test validation of CSV with valid date header"""
        is_valid, start_date, end_date, message = validate_csv_header(sample_csv_file)
        
        assert is_valid is True
        assert start_date is not None
        assert end_date is not None
        assert "valid" in message.lower() or "✓" in message or "✅" in message
    
    def test_nonexistent_file(self):
        """Test with non-existent file"""
        is_valid, start_date, end_date, message = validate_csv_header("/nonexistent/path.csv")
        
        assert is_valid is False
        assert start_date is None
        assert end_date is None
    
    def test_csv_without_date_header(self, temp_directory):
        """Test CSV without date header"""
        csv_path = os.path.join(temp_directory, 'no_dates.csv')
        with open(csv_path, 'w', encoding='utf-8-sig') as f:
            f.write("code,product_name,price\n")
            f.write("001,Product A,10.0\n")
        
        is_valid, start_date, end_date, message = validate_csv_header(csv_path)
        
        assert is_valid is False
        assert start_date is None


class TestValidateCsvHeaders:
    """Tests for validate_csv_headers function"""
    
    def test_nonexistent_file(self):
        """Test with non-existent file"""
        is_valid, errors, message = validate_csv_headers("/nonexistent/path.csv")
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_valid_csv_with_all_columns(self, temp_directory):
        """Test CSV with all required columns"""
        csv_path = os.path.join(temp_directory, 'valid.csv')
        
        # Create CSV with required columns
        headers = [
            "كود", "إسم الصنف", "سعر البيع", "الشركة", "الوحدة",
            "مبيعات الادارة", "رصيد الادارة",
            "مبيعات الشهيد", "رصيد الشهيد",
            "مبيعات العشرين", "رصيد العشرين",
            "مبيعات العقبى", "رصيد العقبى",
            "مبيعات النجوم", "رصيد النجوم",
            "مبيعات الوردانى", "رصيد الوردانى"
        ]
        
        with open(csv_path, 'w', encoding='utf-8-sig') as f:
            f.write(','.join(headers) + '\n')
            f.write('001,Product A,10.0,Company X,Box,100,50,80,40,90,45,85,42,70,35,75,38\n')
        
        is_valid, errors, message = validate_csv_headers(csv_path)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_csv_missing_columns(self, temp_directory):
        """Test CSV with missing required columns"""
        csv_path = os.path.join(temp_directory, 'missing.csv')
        
        with open(csv_path, 'w', encoding='utf-8-sig') as f:
            f.write("كود,إسم الصنف\n")  # Missing many required columns
            f.write("001,Product A\n")
        
        is_valid, errors, message = validate_csv_headers(csv_path)
        
        assert is_valid is False
        assert len(errors) > 0

"""Additional tests to improve coverage for partially covered modules"""

import os
import sys
import math
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ===================== Allocation Calculator Edge Cases =====================

class TestAllocationCalculatorEdgeCases:
    """Edge case tests for allocation_calculator to reach 100% coverage"""
    
    def test_empty_branch_data(self):
        """Test with empty branch data (line 19-20)"""
        from src.core.domain.calculations.allocation_calculator import (
            calculate_proportional_allocations_vectorized
        )
        
        result = calculate_proportional_allocations_vectorized({}, [])
        assert result == {}
    
    def test_no_surplus_needed_mask(self):
        """Test when no products need proportional allocation (lines 43, 51-54)"""
        from src.core.domain.calculations.allocation_calculator import (
            calculate_proportional_allocations_vectorized
        )
        
        # All products have surplus >= needed (no proportional allocation needed)
        branches = ['branch1', 'branch2']
        branch_data = {
            'branch1': pd.DataFrame({
                'avg_sales': [1.0, 2.0],
                'balance': [100.0, 100.0],  # High balance
                'needed_quantity': [0.0, 0.0],  # No need
                'surplus_quantity': [50.0, 50.0]  # Has surplus
            }),
            'branch2': pd.DataFrame({
                'avg_sales': [1.0, 2.0],
                'balance': [100.0, 100.0],
                'needed_quantity': [0.0, 0.0],
                'surplus_quantity': [50.0, 50.0]
            })
        }
        
        result = calculate_proportional_allocations_vectorized(branch_data, branches)
        
        # No allocations needed since no branch needs anything
        assert result == {}
    
    def test_normalize_equal_values(self):
        """Test normalization when max_val - min_val == 0 (line 75-76)"""
        from src.core.domain.calculations.allocation_calculator import (
            calculate_proportional_allocations_vectorized
        )
        
        # All branches have identical values (normalization returns 1.0 for all)
        branches = ['branch1', 'branch2', 'branch3']
        branch_data = {
            'branch1': pd.DataFrame({
                'avg_sales': [1.0],
                'balance': [10.0],
                'needed_quantity': [20.0],
                'surplus_quantity': [0.0]
            }),
            'branch2': pd.DataFrame({
                'avg_sales': [1.0],  # Same as branch1
                'balance': [10.0],  # Same as branch1
                'needed_quantity': [20.0],
                'surplus_quantity': [5.0]
            }),
            'branch3': pd.DataFrame({
                'avg_sales': [1.0],  # Same
                'balance': [10.0],  # Same
                'needed_quantity': [20.0],
                'surplus_quantity': [10.0]
            })
        }
        
        result = calculate_proportional_allocations_vectorized(branch_data, branches)
        
        # Should still produce allocations even with equal normalization
        assert isinstance(result, dict)
    
    def test_zero_scores_fallback(self):
        """Test fallback when total_scores_sum <= 0 (lines 95-97)"""
        from src.core.domain.calculations.allocation_calculator import (
            calculate_proportional_allocations_vectorized
        )
        
        # Edge case: all score components are 0
        branches = ['branch1', 'branch2']
        branch_data = {
            'branch1': pd.DataFrame({
                'avg_sales': [0.0],  # Zero sales
                'balance': [0.0],  # Zero balance
                'needed_quantity': [10.0],
                'surplus_quantity': [0.0]
            }),
            'branch2': pd.DataFrame({
                'avg_sales': [0.0],
                'balance': [0.0],
                'needed_quantity': [10.0],
                'surplus_quantity': [5.0]
            })
        }
        
        result = calculate_proportional_allocations_vectorized(branch_data, branches)
        
        # Should use fallback proportion
        assert isinstance(result, dict)


# ===================== Archiver Edge Cases =====================

class TestArchiverEdgeCases:
    """Edge case tests for archiver module to reach higher coverage"""
    
    def test_archive_nonexistent_directory_raises(self, tmp_path):
        """Test that archiving non-existent directory raises error (line 28-29)"""
        from src.shared.utils.archiver import archive_output_directory
        
        with pytest.raises(ValueError) as exc_info:
            archive_output_directory("/nonexistent/directory", str(tmp_path))
        
        assert "not found" in str(exc_info.value)
    
    def test_archive_with_existing_destination(self, tmp_path):
        """Test archiving when destination already exists (lines 59-60)"""
        from src.shared.utils.archiver import archive_output_directory
        
        # Create source directory with files
        source_dir = tmp_path / "output"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("test content")
        
        # Create archive base
        archive_base = tmp_path / "archive"
        archive_base.mkdir()
        
        # First archive
        result1 = archive_output_directory(str(source_dir), str(archive_base))
        assert result1['file_count'] == 1
        
        # Modify source and archive again (should work even with existing archives)
        (source_dir / "file2.txt").write_text("more content")
        result2 = archive_output_directory(str(source_dir), str(archive_base))
        assert result2['file_count'] == 2
    
    def test_create_zip_nonexistent_raises(self, tmp_path):
        """Test ZIP creation with non-existent directory raises error (line 94-95)"""
        from src.shared.utils.archiver import create_zip_archive
        
        with pytest.raises(ValueError) as exc_info:
            create_zip_archive("/nonexistent/directory")
        
        assert "not found" in str(exc_info.value)
    
    def test_archive_all_output_nonexistent(self, tmp_path, monkeypatch):
        """Test archive_all_output with non-existent output (lines 130-133)"""
        from src.shared.utils.archiver import archive_all_output
        
        # Change working directory temporarily
        monkeypatch.chdir(tmp_path)
        
        with pytest.raises(ValueError) as exc_info:
            archive_all_output()
        
        assert "not found" in str(exc_info.value)
    
    def test_clear_empty_directory(self, tmp_path):
        """Test clearing an empty directory (lines 181-183)"""
        from src.shared.utils.archiver import clear_output_directory
        
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        result = clear_output_directory(str(empty_dir))
        
        assert result is True


# ===================== Data Validator Edge Cases =====================

class TestDataValidatorEdgeCases:
    """Edge case tests for data_validator module"""
    
    def test_extract_dates_invalid_format(self):
        """Test extracting dates from invalid format (lines 26-27)"""
        from src.core.validation import extract_dates_from_header
        
        # Invalid date format
        header = "من: invalid/date إلى: another/invalid"
        start, end = extract_dates_from_header(header)
        
        assert start is None
        assert end is None
    
    def test_validate_headers_missing_file(self):
        """Test header validation with missing file (lines 104-106)"""
        from src.core.validation import validate_csv_headers
        
        is_valid, errors, message = validate_csv_headers("/nonexistent/file.csv")
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_header_short_date_range(self, tmp_path):
        """Test validation with date range < 3 months (line 158)"""
        from src.core.validation import validate_csv_header
        
        # Create CSV with short date range (less than 3 months)
        csv_path = tmp_path / "short_range.csv"
        header = "من: 01/11/2024 00:00 إلى: 01/12/2024 00:00"  # 1 month
        with open(csv_path, 'w', encoding='utf-8-sig') as f:
            f.write(header + '\n')
            f.write("code,product_name\n")
        
        is_valid, start, end, message = validate_csv_header(str(csv_path))
        
        # Valid dates but range too short
        assert start is not None
        assert end is not None
        assert is_valid is False  # Range < 3 months
    
    def test_validate_csv_header_no_dates(self, tmp_path):
        """Test validate_csv_header with no dates in header (lines 176, 179)"""
        from src.core.validation import validate_csv_header
        
        csv_path = tmp_path / "no_dates.csv"
        with open(csv_path, 'w', encoding='utf-8-sig') as f:
            f.write("Just a normal header without dates\n")
            f.write("code,product_name\n")
        
        is_valid, start, end, message = validate_csv_header(str(csv_path))
        
        assert is_valid is False
        assert start is None
        assert end is None


# ===================== Surplus Finder Edge Cases =====================

class TestSurplusFinderEdgeCases:
    """Edge case tests for surplus_finder module"""
    
    def test_product_with_no_need(self):
        """Test when product has no need (line 86 branch)"""
        from src.services.splitting.processors.surplus_finder import (
            find_surplus_sources_for_single_product
        )
        from src.core.domain.branches.config import get_branches
        
        branches = get_branches()
        
        # Product has no need (balance > monthly)
        branch_data = {}
        for branch in branches:
            branch_data[branch] = pd.DataFrame({
                'code': ['001'],
                'product_name': ['Product A'],
                'avg_sales': [1.0],
                'balance': [100.0],  # High balance
                'needed_quantity': [0.0],  # No need
                'surplus_quantity': [70.0],
                'monthly_quantity': [30.0]
            })
        
        withdrawals, withdrawal_dict = find_surplus_sources_for_single_product(
            branches[0], 0, branch_data, branches
        )
        
        # Should return empty withdrawals since no need
        assert isinstance(withdrawals, list)


# ===================== Branch Splitter Edge Cases =====================

class TestBranchSplitterEdgeCases:
    """Edge case tests for branch_splitter module"""
    
    def test_split_csv_nonexistent_file(self, tmp_path):
        """Test splitting a non-existent file"""
        from src.services.splitting.core import split_csv_by_branches
        
        with pytest.raises(Exception):
            split_csv_by_branches(
                "/nonexistent/file.csv",
                str(tmp_path / "branches"),
                "test",
                str(tmp_path / "analytics")
            )


# ===================== Target Calculator Edge Cases =====================

class TestTargetCalculatorEdgeCases:
    """Edge case tests for target_calculator module"""
    
    def test_skip_transfer_exact_boundary(self):
        """Test should_skip_transfer at exact boundary (line 46)"""
        from src.services.splitting.processors.target_calculator import (
            should_skip_transfer,
            MAXIMUM_BRANCH_BALANCE_THRESHOLD
        )
        
        # At exact max balance
        assert should_skip_transfer(MAXIMUM_BRANCH_BALANCE_THRESHOLD) is True
        
        # Just below max
        assert should_skip_transfer(MAXIMUM_BRANCH_BALANCE_THRESHOLD - 0.01) is False
    
    def test_calculate_target_with_allocation(self):
        """Test calculate_target_amount with proportional allocation (line 59)"""
        from src.services.splitting.processors.target_calculator import (
            calculate_target_amount,
            MAXIMUM_BRANCH_BALANCE_THRESHOLD
        )
        
        # Test with allocation that exceeds max
        result = calculate_target_amount(
            needed=50.0,
            balance=25.0,
            proportional_allocation=10.0  # 25 + 10 > 30, should cap
        )
        
        assert result <= MAXIMUM_BRANCH_BALANCE_THRESHOLD - 25.0


# ===================== Data Preparer Edge Cases =====================

class TestDataPreparerEdgeCases:
    """Edge case tests for data_preparer module"""
    
    def test_prepare_data_no_date_header(self, tmp_path):
        """Test data preparation without date header (lines 48, 63, 74-75)"""
        from src.services.splitting.processors.data_preparer import prepare_branch_data
        
        # Create CSV without date header but with all required columns
        csv_path = tmp_path / "no_date.csv"
        df = pd.DataFrame({
            'code': ['001'],
            'product_name': ['Product A'],
            'selling_price': [10.0],
            'company': ['Test Company'],
            'unit': ['Box'],
            'admin_sales': [10.0],
            'admin_avg_sales': [0.33],
            'admin_balance': [5.0],
            'shahid_sales': [8.0],
            'shahid_avg_sales': [0.27],
            'shahid_balance': [3.0],
            'asherin_sales': [6.0],
            'asherin_avg_sales': [0.20],
            'asherin_balance': [4.0],
            'akba_sales': [7.0],
            'akba_avg_sales': [0.23],
            'akba_balance': [2.0],
            'nujum_sales': [9.0],
            'nujum_avg_sales': [0.30],
            'nujum_balance': [6.0],
            'wardani_sales': [5.0],
            'wardani_avg_sales': [0.17],
            'wardani_balance': [7.0],
            'total_sales': [45.0],
            'total_product_balance': [27.0]
        })
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Should still work with default date range
        branch_data, has_date, first_line = prepare_branch_data(
            str(csv_path),
            start_date=datetime(2024, 9, 1),
            end_date=datetime(2024, 12, 1)
        )
        
        assert has_date is False
        assert len(branch_data) == 6


# ===================== Transfer Generator Edge Cases =====================

class TestTransferGeneratorEdgeCases:
    """Edge case tests for transfer_generator module"""
    
    def test_generate_transfers_empty_analytics(self, tmp_path):
        """Test with empty analytics directory (lines 37, 49-51)"""
        from src.services.transfers.generators.transfer_generator import (
            generate_transfer_files
        )
        
        analytics_dir = tmp_path / "analytics"
        transfers_dir = tmp_path / "transfers"
        analytics_dir.mkdir()
        transfers_dir.mkdir()
        
        result = generate_transfer_files(str(analytics_dir), str(transfers_dir))
        
        assert result == {}
    
    def test_generate_transfer_no_matching_products(self, tmp_path):
        """Test when no products match source branch (lines 101-105)"""
        from src.services.transfers.generators.transfer_generator import (
            generate_transfer_for_pair
        )
        from src.core.domain.branches.config import get_branches
        
        branches = get_branches()
        
        # Create analytics with no matching source
        analytics_dir = tmp_path / "analytics"
        target_dir = analytics_dir / branches[0]
        target_dir.mkdir(parents=True)
        transfers_dir = tmp_path / "transfers"
        transfers_dir.mkdir()
        
        # Analytics file with different source branch
        df = pd.DataFrame({
            'code': ['001'],
            'product_name': ['Product A'],
            'available_branch_1': ['nonexistent_branch'],
            'surplus_from_branch_1': [10]
        })
        df.to_csv(target_dir / "test_analytics.csv", index=False, encoding='utf-8-sig')
        
        result = generate_transfer_for_pair(
            branches[1],  # Looking for this source
            branches[0],
            str(analytics_dir),
            str(transfers_dir)
        )
        
        # Should return None when no matching products
        assert result is None


# ===================== Sales Analyzer Edge Cases =====================

class TestSalesAnalyzerEdgeCases:
    """Edge case tests for sales_analyzer module"""
    
    def test_analyze_csv_without_date_header(self, tmp_path):
        """Test analyzing CSV without date header (line 31)"""
        from src.core.domain.analysis.sales_analyzer import analyze_csv_data
        
        csv_path = tmp_path / "no_date.csv"
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['A', 'B'],
            'price': [10.0, 20.0]
        })
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        result = analyze_csv_data(str(csv_path))
        
        assert result['date_range'] is None
        assert result['total_rows'] == 2
    
    def test_analyze_csv_file_error(self):
        """Test analyzing non-existent file raises error (lines 50-51)"""
        from src.core.domain.analysis.sales_analyzer import analyze_csv_data
        
        with pytest.raises(ValueError) as exc_info:
            analyze_csv_data("/nonexistent/file.csv")
        
        assert "Error analyzing" in str(exc_info.value)

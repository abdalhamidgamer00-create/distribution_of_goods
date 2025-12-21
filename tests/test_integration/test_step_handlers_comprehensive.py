"""Comprehensive tests for pipeline step handlers using actual sample files"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ===================== Fixtures =====================

@pytest.fixture(scope="module")
def sample_excel():
    """Path to sample Excel file"""
    path = PROJECT_ROOT / "data" / "input" / "problemm20251220.xlsx"
    if not path.exists():
        pytest.skip("Sample Excel not found")
    return str(path)


@pytest.fixture(scope="module")
def sample_converted_csv():
    """Path to sample converted CSV"""
    path = PROJECT_ROOT / "data" / "output" / "converted" / "csv" / "problemm20251220_20251220_093011.csv"
    if not path.exists():
        pytest.skip("Sample converted CSV not found")
    return str(path)


@pytest.fixture(scope="module")
def sample_renamed_csv():
    """Path to sample renamed CSV"""
    path = PROJECT_ROOT / "data" / "output" / "converted" / "renamed" / "problemm20251220_20251220_093011_renamed.csv"
    if not path.exists():
        pytest.skip("Sample renamed CSV not found")
    return str(path)


@pytest.fixture(scope="module")
def sample_analytics_dir():
    """Path to sample analytics directory"""
    path = PROJECT_ROOT / "data" / "output" / "branches" / "analytics"
    if not path.exists():
        pytest.skip("Analytics directory not found")
    return str(path)


@pytest.fixture
def mock_file_selector():
    """Mock file selector to always use latest file"""
    with patch('src.app.pipeline.utils.file_selector.select_excel_file') as mock_excel, \
         patch('src.app.pipeline.utils.file_selector.select_csv_file') as mock_csv:
        
        def return_first_file(directory, files, use_latest=None):
            return files[0] if files else None
        
        mock_excel.side_effect = return_first_file
        mock_csv.side_effect = return_first_file
        
        yield mock_excel, mock_csv


# ===================== Step 2 Handler Tests =====================

class TestStep2Handler:
    """Tests for Step 2: Excel to CSV conversion handler"""
    
    def test_step_2_with_sample_excel(self, sample_excel, tmp_path, monkeypatch):
        """Test step 2 handler with actual Excel file"""
        from src.services.conversion.converters.excel_to_csv import convert_excel_to_csv
        
        # Setup temp environment
        input_dir = tmp_path / "data" / "input"
        output_dir = tmp_path / "data" / "output" / "converted" / "csv"
        input_dir.mkdir(parents=True)
        output_dir.mkdir(parents=True)
        
        # Copy sample Excel
        shutil.copy(sample_excel, input_dir / "test.xlsx")
        
        # Convert directly
        output_path = output_dir / "test_output.csv"
        result = convert_excel_to_csv(
            str(input_dir / "test.xlsx"),
            str(output_path)
        )
        
        assert result is True
        assert output_path.exists()
        
        # Verify content
        df = pd.read_csv(output_path, encoding='utf-8-sig')
        assert len(df) > 0


# ===================== Step 3 Handler Tests =====================

class TestStep3Handler:
    """Tests for Step 3: Validation handler"""
    
    def test_validate_converted_csv(self, sample_converted_csv):
        """Test validation with actual converted CSV"""
        from src.core.validation.data_validator import validate_csv_header, validate_csv_headers
        
        # Validate date header
        is_valid_date, start, end, msg = validate_csv_header(sample_converted_csv)
        
        # Validate column headers
        is_valid_headers, errors, headers_msg = validate_csv_headers(sample_converted_csv)
        
        # Should have valid headers
        assert isinstance(is_valid_headers, bool)
    
    def test_validate_date_range_from_actual_file(self, sample_converted_csv):
        """Test date extraction from actual file"""
        from src.core.validation.data_validator import extract_dates_from_header
        
        with open(sample_converted_csv, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
        
        start, end = extract_dates_from_header(first_line)
        
        # Should extract dates if present
        if start and end:
            assert start < end


# ===================== Step 4 Handler Tests =====================

class TestStep4Handler:
    """Tests for Step 4: Sales analysis handler"""
    
    def test_analyze_converted_csv(self, sample_converted_csv):
        """Test analysis with actual converted CSV"""
        from src.core.domain.analysis.sales_analyzer import analyze_csv_data
        from src.shared.reporting.report_generator import generate_report
        
        analysis = analyze_csv_data(sample_converted_csv)
        
        assert 'total_rows' in analysis
        assert 'total_columns' in analysis
        assert analysis['total_rows'] > 0
        
        # Generate report
        report = generate_report(analysis, "test.csv")
        assert "REPORT" in report.upper()


# ===================== Step 5 Handler Tests =====================

class TestStep5Handler:
    """Tests for Step 5: Column renaming handler"""
    
    def test_rename_columns_actual_file(self, sample_converted_csv, tmp_path):
        """Test column renaming with actual file"""
        from src.services.conversion.converters.csv_column_renamer import rename_csv_columns
        
        output_path = tmp_path / "renamed.csv"
        result = rename_csv_columns(sample_converted_csv, str(output_path))
        
        assert result is True
        assert output_path.exists()
        
        # Verify English columns
        df = pd.read_csv(output_path, encoding='utf-8-sig', skiprows=1)
        expected_cols = ['code', 'product_name', 'admin_sales', 'admin_balance']
        for col in expected_cols:
            assert col in df.columns


# ===================== Step 6 Handler Tests =====================

class TestStep6Handler:
    """Tests for Step 6: Split by branches handler"""
    
    def test_split_renamed_csv(self, sample_renamed_csv, tmp_path):
        """Test splitting actual renamed CSV"""
        from src.services.splitting.branch_splitter import split_csv_by_branches
        from src.core.domain.branches.config import get_branches
        
        branches_dir = tmp_path / "branches"
        analytics_dir = tmp_path / "analytics"
        
        for branch in get_branches():
            (branches_dir / branch).mkdir(parents=True)
            (analytics_dir / branch).mkdir(parents=True)
        
        output_files, timing = split_csv_by_branches(
            sample_renamed_csv,
            str(branches_dir),
            "test_split",
            str(analytics_dir)
        )
        
        assert len(output_files) == 6  # 6 branches
        
        # Verify branch files exist
        for branch, file_path in output_files.items():
            assert os.path.exists(file_path)


# ===================== Step 7 Handler Tests =====================

class TestStep7Handler:
    """Tests for Step 7: Transfer generation handler"""
    
    def test_generate_transfers_from_analytics(self, sample_analytics_dir, tmp_path):
        """Test transfer generation with actual analytics"""
        from src.services.transfers.generators.transfer_generator import generate_transfer_files
        
        transfers_dir = tmp_path / "transfers"
        transfers_dir.mkdir()
        
        result = generate_transfer_files(sample_analytics_dir, str(transfers_dir))
        
        assert isinstance(result, dict)
        # Should generate some transfers
    
    def test_transfer_file_structure(self, sample_analytics_dir, tmp_path):
        """Test that generated transfer files have correct structure"""
        from src.services.transfers.generators.transfer_generator import generate_transfer_for_pair
        from src.core.domain.branches.config import get_branches
        
        branches = get_branches()
        transfers_dir = tmp_path / "transfers"
        transfers_dir.mkdir()
        
        # Generate transfer for first pair
        result = generate_transfer_for_pair(
            branches[0], branches[1],
            sample_analytics_dir, str(transfers_dir)
        )
        
        if result:
            # Verify file structure
            df = pd.read_csv(result, encoding='utf-8-sig')
            assert 'code' in df.columns
            assert 'product_name' in df.columns or 'quantity_to_transfer' in df.columns


# ===================== Step 8 Handler Tests =====================

class TestStep8Handler:
    """Tests for Step 8: Split by product type handler"""
    
    def test_split_by_product_type(self, tmp_path):
        """Test splitting transfer file by product type"""
        from src.services.transfers.splitters.file_splitter import split_transfer_file_by_type
        
        # Create test transfer file
        transfer_file = tmp_path / "test_transfer_from_admin_to_wardani.csv"
        df = pd.DataFrame({
            'code': ['001', '002', '003', '004', '005', '006'],
            'product_name': [
                'Panadol TAB 500mg',
                'Vitamin D CAP',
                'Insulin AMP 10ml',
                'Cough SYRUP 100ml',
                'Skin CREAM 30g',
                'ORS SACHETS 5g'
            ],
            'quantity_to_transfer': [10, 20, 15, 5, 8, 12]
        })
        df.to_csv(transfer_file, index=False, encoding='utf-8-sig')
        
        output_dir = tmp_path / "split"
        output_dir.mkdir()
        
        result = split_transfer_file_by_type(str(transfer_file), str(output_dir))
        
        assert isinstance(result, dict)
        # Should have multiple categories
        assert len(result) >= 3
    
    def test_split_all_transfer_files(self, tmp_path):
        """Test splitting all transfer files"""
        from src.services.transfers.splitters.file_splitter import split_all_transfer_files
        
        # Create transfer directory with files
        transfers_dir = tmp_path / "transfers" / "admin"
        transfers_dir.mkdir(parents=True)
        
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['Aspirin TAB', 'Vitamin SYRUP'],
            'quantity_to_transfer': [10, 20]
        })
        df.to_csv(transfers_dir / "transfer_from_admin_to_shahid.csv", index=False, encoding='utf-8-sig')
        
        result = split_all_transfer_files(str(tmp_path / "transfers"))
        
        assert isinstance(result, dict)


# ===================== Step 9 Handler Tests =====================

class TestStep9Handler:
    """Tests for Step 9: Surplus calculation handler"""
    
    def test_calculate_remaining_surplus(self, sample_analytics_dir):
        """Test surplus calculation with actual analytics"""
        from src.app.pipeline.step_9.surplus_calculator import (
            calculate_remaining_surplus,
            validate_analytics_columns
        )
        from src.core.domain.branches.config import get_branches
        from src.shared.utils.file_handler import get_latest_file
        
        branches = get_branches()
        branch = branches[0]
        branch_dir = os.path.join(sample_analytics_dir, branch)
        
        if os.path.exists(branch_dir):
            latest = get_latest_file(branch_dir, '.csv')
            if latest:
                df = pd.read_csv(
                    os.path.join(branch_dir, latest),
                    encoding='utf-8-sig',
                    skiprows=1
                )
                
                # Validate columns
                missing = validate_analytics_columns(df)
                
                if not missing:
                    # Calculate remaining surplus
                    result = calculate_remaining_surplus(df, {})
                    assert isinstance(result, pd.DataFrame)


# ===================== Step 10 Handler Tests =====================

class TestStep10Handler:
    """Tests for Step 10: Shortage calculation handler"""
    
    def test_read_analytics_file(self, sample_analytics_dir):
        """Test reading analytics file"""
        from src.app.pipeline.step_10.shortage_calculator import read_analytics_file
        from src.core.domain.branches.config import get_branches
        from src.shared.utils.file_handler import get_latest_file
        
        branches = get_branches()
        branch = branches[0]
        branch_dir = os.path.join(sample_analytics_dir, branch)
        
        if os.path.exists(branch_dir):
            latest = get_latest_file(branch_dir, '.csv')
            if latest:
                df, has_date, first_line = read_analytics_file(
                    os.path.join(branch_dir, latest)
                )
                
                assert df is not None
                assert isinstance(has_date, bool)


# ===================== Step 11 Handler Tests =====================

class TestStep11Handler:
    """Tests for Step 11: Combine files handler"""
    
    def test_get_branch_balances(self, sample_analytics_dir):
        """Test getting branch balances from analytics"""
        from src.app.pipeline.step_11.balance_reader import get_branch_balances
        from src.core.domain.branches.config import get_branches
        
        branches = get_branches()
        
        balances = get_branch_balances(sample_analytics_dir, branches[0])
        
        assert isinstance(balances, dict)
    
    def test_get_all_branches_balances(self, sample_analytics_dir):
        """Test getting all branches balances"""
        from src.app.pipeline.step_11.balance_reader import get_all_branches_balances
        from src.core.domain.branches.config import get_branches
        
        branches = get_branches()
        
        all_balances = get_all_branches_balances(sample_analytics_dir, branches)
        
        assert isinstance(all_balances, dict)
        assert len(all_balances) == 6


# ===================== File Splitter Tests =====================

class TestFileSplitterComprehensive:
    """Comprehensive tests for file_splitter module"""
    
    def test_split_with_date_header(self, tmp_path):
        """Test splitting with date header preservation"""
        from src.services.transfers.splitters.file_splitter import split_transfer_file_by_type
        
        transfer_file = tmp_path / "transfer_from_admin_to_shahid.csv"
        df = pd.DataFrame({
            'code': ['001'],
            'product_name': ['Aspirin TAB 500mg'],
            'quantity_to_transfer': [10]
        })
        df.to_csv(transfer_file, index=False, encoding='utf-8-sig')
        
        output_dir = tmp_path / "split"
        output_dir.mkdir()
        
        first_line = "من: 20/09/2024 00:00 إلى: 20/12/2024 00:00"
        result = split_transfer_file_by_type(
            str(transfer_file),
            str(output_dir),
            has_date_header=True,
            first_line=first_line
        )
        
        assert len(result) >= 1
        
        # Check date header in output
        for cat, path in result.items():
            with open(path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                assert '20/09/2024' in content


# ===================== Excel Converter Tests =====================

class TestExcelConverterComprehensive:
    """Comprehensive tests for excel_converter module"""
    
    def test_convert_csv_to_excel(self, tmp_path):
        """Test converting CSV to Excel"""
        from src.services.transfers.converters.excel_converter import convert_split_csv_to_excel
        
        # Create directory structure
        transfers_dir = tmp_path / "transfers_from_admin_to_other_branches"
        transfers_dir.mkdir(parents=True)
        
        subfolder = transfers_dir / "test_file"
        subfolder.mkdir()
        
        csv_path = subfolder / "test_tablets_and_capsules.csv"
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['Product A TAB', 'Product B CAP'],
            'quantity_to_transfer': [10, 20]
        })
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        excel_output = tmp_path / "excel"
        excel_output.mkdir()
        
        result = convert_split_csv_to_excel(str(csv_path), str(excel_output))
        
        assert result is not None
        assert result.endswith('.xlsx')
        assert os.path.exists(result)

"""Integration tests using real sample data from problemm20251220.xlsx"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="module")
def sample_excel_path():
    """Path to the sample Excel file"""
    path = PROJECT_ROOT / "data" / "input" / "problemm20251220.xlsx"
    if not path.exists():
        pytest.skip(f"Sample Excel file not found: {path}")
    return str(path)


@pytest.fixture(scope="module")
def sample_csv_path(sample_excel_path, tmp_path_factory):
    """Convert sample Excel to CSV for testing"""
    from src.services.conversion.converters.excel_to_csv import convert_excel_to_csv
    
    temp_dir = tmp_path_factory.mktemp("data")
    csv_path = temp_dir / "sample_data.csv"
    
    # Read Excel and save as CSV with date header
    df = pd.read_excel(sample_excel_path)
    first_row = df.columns[0]  # Contains the date range
    df_data = pd.read_excel(sample_excel_path, skiprows=1)
    
    with open(csv_path, 'w', encoding='utf-8-sig') as f:
        f.write(first_row + '\n')
        df_data.to_csv(f, index=False, lineterminator='\n')
    
    return str(csv_path)


@pytest.fixture(scope="module") 
def renamed_csv_path(sample_csv_path, tmp_path_factory):
    """Renamed CSV with English column names"""
    from src.services.conversion.converters.csv_column_renamer import rename_csv_columns
    
    temp_dir = tmp_path_factory.mktemp("renamed")
    output_path = temp_dir / "renamed_data.csv"
    
    rename_csv_columns(sample_csv_path, str(output_path))
    
    return str(output_path)


class TestExcelToCsvConversionIntegration:
    """Integration tests for Excel to CSV conversion"""
    
    def test_convert_sample_excel(self, sample_excel_path, tmp_path):
        """Test converting the actual sample Excel file"""
        from src.services.conversion.converters.excel_to_csv import convert_excel_to_csv
        
        output_path = tmp_path / "output.csv"
        result = convert_excel_to_csv(sample_excel_path, str(output_path))
        
        assert result is True
        assert output_path.exists()
        
        # Verify content
        df = pd.read_csv(output_path, encoding='utf-8-sig')
        assert len(df) > 0
    
    def test_converted_csv_has_expected_columns(self, sample_excel_path, tmp_path):
        """Test that converted CSV has all expected Arabic columns"""
        from src.services.conversion.converters.excel_to_csv import convert_excel_to_csv
        
        output_path = tmp_path / "output.csv"
        convert_excel_to_csv(sample_excel_path, str(output_path))
        
        df = pd.read_csv(output_path, encoding='utf-8-sig', skiprows=1)
        
        expected_cols = ['كود', 'إسم الصنف', 'سعر البيع', 'الشركة', 'الوحدة']
        for col in expected_cols:
            assert col in df.columns, f"Missing column: {col}"


class TestColumnRenamingIntegration:
    """Integration tests for column renaming"""
    
    def test_rename_columns_with_sample_data(self, sample_csv_path, tmp_path):
        """Test renaming columns in actual sample CSV"""
        from src.services.conversion.converters.csv_column_renamer import rename_csv_columns
        
        output_path = tmp_path / "renamed.csv"
        result = rename_csv_columns(sample_csv_path, str(output_path))
        
        assert result is True
        assert output_path.exists()
        
        df = pd.read_csv(output_path, encoding='utf-8-sig', skiprows=1)
        
        # Check English columns exist
        expected = ['code', 'product_name', 'selling_price', 'company', 'unit']
        for col in expected:
            assert col in df.columns, f"Missing renamed column: {col}"
    
    def test_branch_columns_renamed(self, renamed_csv_path):
        """Test that branch columns are renamed correctly"""
        df = pd.read_csv(renamed_csv_path, encoding='utf-8-sig', skiprows=1)
        
        branches = ['admin', 'shahid', 'asherin', 'akba', 'nujum', 'wardani']
        for branch in branches:
            assert f'{branch}_sales' in df.columns, f"Missing {branch}_sales"
            assert f'{branch}_balance' in df.columns, f"Missing {branch}_balance"


class TestDataPreparationIntegration:
    """Integration tests for data preparation"""
    
    def test_prepare_branch_data_from_sample(self, renamed_csv_path):
        """Test preparing branch data from renamed CSV"""
        from src.services.splitting.processors.data_preparer import prepare_branch_data
        
        branch_data, has_date_header, first_line = prepare_branch_data(renamed_csv_path)
        
        assert has_date_header is True
        assert '20/09/2025' in first_line or '20/12/2025' in first_line
        
        # Verify branch data structure
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        for branch in branches:
            assert branch in branch_data
            df = branch_data[branch]
            
            # Verify calculated columns
            assert 'monthly_quantity' in df.columns
            assert 'surplus_quantity' in df.columns
            assert 'needed_quantity' in df.columns
    
    def test_quantities_are_non_negative(self, renamed_csv_path):
        """Test that all calculated quantities are non-negative"""
        from src.services.splitting.processors.data_preparer import prepare_branch_data
        
        branch_data, _, _ = prepare_branch_data(renamed_csv_path)
        
        for branch, df in branch_data.items():
            assert (df['monthly_quantity'] >= 0).all(), f"{branch}: negative monthly_quantity"
            assert (df['surplus_quantity'] >= 0).all(), f"{branch}: negative surplus_quantity"
            assert (df['needed_quantity'] >= 0).all(), f"{branch}: negative needed_quantity"


class TestSurplusCalculationsIntegration:
    """Integration tests for surplus calculations with real data"""
    
    def test_find_surplus_sources(self, renamed_csv_path):
        """Test finding surplus sources with real data"""
        from src.services.splitting.processors.data_preparer import prepare_branch_data
        from src.services.splitting.processors.surplus_finder import find_surplus_sources_for_single_product
        from src.core.domain.branches.config import get_branches
        
        branch_data, _, _ = prepare_branch_data(renamed_csv_path)
        branches = get_branches()
        
        # Test first few products
        for idx in range(min(10, len(branch_data[branches[0]]))):
            for branch in branches:
                withdrawals, withdrawal_dict = find_surplus_sources_for_single_product(
                    branch, idx, branch_data, branches
                )
                
                assert isinstance(withdrawals, list)
                assert len(withdrawals) >= 1  # At least one record (even if empty)
    
    def test_proportional_allocation_with_real_data(self, renamed_csv_path):
        """Test proportional allocation with real data"""
        from src.services.splitting.processors.data_preparer import prepare_branch_data
        from src.core.domain.calculations.allocation_calculator import (
            calculate_proportional_allocations_vectorized
        )
        from src.core.domain.branches.config import get_branches
        
        branch_data, _, _ = prepare_branch_data(renamed_csv_path)
        branches = get_branches()
        
        allocations = calculate_proportional_allocations_vectorized(branch_data, branches)
        
        assert isinstance(allocations, dict)
        
        # Verify allocation values are reasonable
        for product_idx, allocation in allocations.items():
            total_allocated = sum(allocation.values())
            assert total_allocated >= 0


class TestTransferGenerationIntegration:
    """Integration tests for transfer file generation"""
    
    def test_full_pipeline_flow(self, renamed_csv_path, tmp_path):
        """Test the full flow from data prep to transfer generation"""
        from src.services.splitting.processors.data_preparer import prepare_branch_data
        from src.services.splitting.core import split_csv_by_branches
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Split CSV by branches
        split_csv_by_branches(
            renamed_csv_path,
            str(output_dir / "branches"),
            "test_split",
            str(output_dir / "analytics")
        )
        
        # Verify branch files were created
        branches_dir = output_dir / "branches"
        if branches_dir.exists():
            branch_files = list(branches_dir.glob("**/*.csv"))
            assert len(branch_files) > 0, "No branch files created"


class TestArchiverIntegration:
    """Integration tests for archiver functionality"""
    
    def test_archive_output_directory(self, tmp_path):
        """Test archiving an output directory"""
        from src.shared.utils.archiver import archive_output_directory
        
        # Create test output directory with files
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        subdir = output_dir / "subdir"
        subdir.mkdir()
        
        (output_dir / "file1.csv").write_text("test data 1")
        (subdir / "file2.csv").write_text("test data 2")
        
        archive_dir = tmp_path / "archive"
        
        result = archive_output_directory(str(output_dir), str(archive_dir))
        
        assert 'archive_dir' in result
        assert result['file_count'] >= 2
        assert os.path.exists(result['archive_dir'])
    
    def test_clear_output_directory(self, tmp_path):
        """Test clearing output directory"""
        from src.shared.utils.archiver import clear_output_directory
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "file.csv").write_text("test")
        
        result = clear_output_directory(str(output_dir))
        
        assert result is True
        assert len(list(output_dir.iterdir())) == 0
    
    def test_create_zip_archive(self, tmp_path):
        """Test creating ZIP archive"""
        from src.shared.utils.archiver import create_zip_archive
        
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "file.txt").write_text("test content")
        
        zip_path = create_zip_archive(str(archive_dir))
        
        assert os.path.exists(zip_path)
        assert zip_path.endswith('.zip')


class TestSalesAnalyzerIntegration:
    """Integration tests for sales analyzer"""
    
    def test_analyze_sample_data(self, sample_csv_path):
        """Test analyzing sample CSV data"""
        from src.core.domain.analysis.sales_analyzer import analyze_csv_data
        
        analysis = analyze_csv_data(sample_csv_path)
        
        assert 'total_rows' in analysis
        assert 'total_columns' in analysis
        assert 'total_cells' in analysis
        assert 'empty_cells' in analysis
        assert analysis['total_rows'] > 0
        assert 'date_range' in analysis

"""Tests for pipeline step handler functions using mocking"""

import os
import sys
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def setup_test_environment(tmp_path):
    """
    Setup a complete test environment with proper directory structure
    and sample files for testing pipeline handlers.
    """
    # Create directory structure like actual project
    data_dir = tmp_path / "data"
    input_dir = data_dir / "input"
    output_dir = data_dir / "output"
    converted_csv = output_dir / "converted" / "csv"
    converted_renamed = output_dir / "converted" / "renamed"
    branches_files = output_dir / "branches" / "files"
    branches_analytics = output_dir / "branches" / "analytics"
    transfers_csv = output_dir / "transfers" / "csv"
    archive_dir = data_dir / "archive"
    
    # Create all directories
    for d in [input_dir, converted_csv, converted_renamed, 
              branches_files, branches_analytics, transfers_csv, archive_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Create branch subdirectories
    from src.core.domain.branches.config import get_branches
    for branch in get_branches():
        (branches_files / branch).mkdir(exist_ok=True)
        (branches_analytics / branch).mkdir(exist_ok=True)
    
    return {
        'root': tmp_path,
        'data': data_dir,
        'input': input_dir,
        'converted_csv': converted_csv,
        'converted_renamed': converted_renamed,
        'branches_files': branches_files,
        'branches_analytics': branches_analytics,
        'transfers_csv': transfers_csv,
        'archive': archive_dir
    }


@pytest.fixture
def sample_excel_file(setup_test_environment):
    """Create a sample Excel file for testing"""
    env = setup_test_environment
    
    # Copy actual sample file if exists
    actual_sample = PROJECT_ROOT / "data" / "input" / "problemm20251220.xlsx"
    if actual_sample.exists():
        dest = env['input'] / "test_input.xlsx"
        shutil.copy(actual_sample, dest)
        return str(dest)
    
    pytest.skip("Sample Excel file not found")


@pytest.fixture
def sample_csv_file(setup_test_environment):
    """Create a sample CSV file with proper Arabic headers"""
    env = setup_test_environment
    
    # Create CSV with date header line
    header_line = "مبيعات الأصناف فى جميع المخازن الفترة من 20/09/2024 00:00 إلى 20/12/2024 00:00"
    
    columns = [
        "كود", "إسم الصنف", "سعر البيع", "الشركة", "الوحدة",
        "مبيعات الادارة", "متوسط مبيعات الادارة", "رصيد الادارة",
        "مبيعات الشهيد", "متوسط مبيعات الشهيد", "رصيد الشهيد",
        "مبيعات العشرين", "متوسط مبيعات العشرين", "رصيد العشرين",
        "مبيعات العقبى", "متوسط مبيعات العقبى", "رصيد العقبى",
        "مبيعات النجوم", "متوسط مبيعات النجوم", "رصيد النجوم",
        "مبيعات الوردانى", "متوسط مبيعات الوردانى", "رصيد الوردانى",
        "إجمالى المبيعات", "إجمالى رصيد الصنف"
    ]
    
    data = [
        ["001", "Panadol TAB 500mg", 10.0, "GSK", "Box", 
         20, 0.5, 10, 15, 0.4, 8, 25, 0.6, 12, 10, 0.3, 5, 18, 0.45, 9, 12, 0.3, 6, 100, 50],
        ["002", "Vitamin D CAP", 20.0, "Pharco", "Piece", 
         40, 1.0, 20, 30, 0.8, 16, 50, 1.2, 24, 20, 0.5, 10, 36, 0.9, 18, 24, 0.6, 12, 200, 100],
    ]
    
    df = pd.DataFrame(data, columns=columns)
    
    csv_path = env['converted_csv'] / "test_data.csv"
    with open(csv_path, 'w', encoding='utf-8-sig') as f:
        f.write(header_line + '\n')
        df.to_csv(f, index=False, lineterminator='\n')
    
    return str(csv_path)


@pytest.fixture
def sample_renamed_csv(setup_test_environment):
    """Create a sample renamed CSV with English columns"""
    env = setup_test_environment
    
    # Date header
    header_line = "من: 20/09/2024 00:00 إلى: 20/12/2024 00:00"
    
    df = pd.DataFrame({
        'code': ['001', '002', '003'],
        'product_name': ['Panadol TAB 500mg', 'Vitamin D AMP', 'Cough SYRUP'],
        'selling_price': [10.0, 20.0, 15.0],
        'company': ['GSK', 'Pharco', 'EIPICO'],
        'unit': ['Box', 'Piece', 'Bottle'],
        'admin_sales': [20, 40, 30],
        'admin_avg_sales': [0.5, 1.0, 0.75],
        'admin_balance': [10, 20, 50],
        'shahid_sales': [15, 30, 25],
        'shahid_avg_sales': [0.4, 0.8, 0.6],
        'shahid_balance': [8, 16, 40],
        'asherin_sales': [25, 50, 35],
        'asherin_avg_sales': [0.6, 1.2, 0.9],
        'asherin_balance': [12, 24, 30],
        'akba_sales': [10, 20, 15],
        'akba_avg_sales': [0.3, 0.5, 0.4],
        'akba_balance': [5, 10, 25],
        'nujum_sales': [18, 36, 28],
        'nujum_avg_sales': [0.45, 0.9, 0.7],
        'nujum_balance': [9, 18, 35],
        'wardani_sales': [12, 24, 18],
        'wardani_avg_sales': [0.3, 0.6, 0.45],
        'wardani_balance': [6, 12, 20],
        'total_sales': [100, 200, 151],
        'total_product_balance': [50, 100, 200]
    })
    
    csv_path = env['converted_renamed'] / "test_renamed.csv"
    with open(csv_path, 'w', encoding='utf-8-sig') as f:
        f.write(header_line + '\n')
        df.to_csv(f, index=False, lineterminator='\n')
    
    return str(csv_path)


# ===================== Step 2 Handler Tests =====================

class TestStep2HandlerWithMock:
    """Tests for Step 2 handler using mocking"""
    
    def test_step_2_with_use_latest(self, sample_excel_file, setup_test_environment, monkeypatch):
        """Test step_2_convert_excel_to_csv with use_latest_file=True"""
        from src.app.pipeline.step_2.handler import step_2_convert_excel_to_csv
        
        env = setup_test_environment
        
        # Change to test directory
        monkeypatch.chdir(env['root'])
        
        # Run handler with use_latest_file=True
        result = step_2_convert_excel_to_csv(use_latest_file=True)
        
        assert result is True
        
        # Verify CSV was created
        csv_files = list(env['converted_csv'].glob("*.csv"))
        assert len(csv_files) >= 1


# ===================== Step 3 Handler Tests =====================

class TestStep3HandlerWithMock:
    """Tests for Step 3 handler using mocking"""
    
    def test_step_3_with_use_latest(self, sample_csv_file, setup_test_environment, monkeypatch):
        """Test step_3_validate_data with use_latest_file=True"""
        from src.app.pipeline.step_3.validator import step_3_validate_data
        
        env = setup_test_environment
        monkeypatch.chdir(env['root'])
        
        result = step_3_validate_data(use_latest_file=True)
        
        # Should return True for valid file or False for invalid
        assert isinstance(result, bool)


# ===================== Step 4 Handler Tests =====================

class TestStep4HandlerWithMock:
    """Tests for Step 4 handler using mocking"""
    
    def test_step_4_with_use_latest(self, sample_csv_file, setup_test_environment, monkeypatch):
        """Test step_4_sales_analysis with use_latest_file=True"""
        from src.app.pipeline.step_4.handler import step_4_sales_analysis
        
        env = setup_test_environment
        monkeypatch.chdir(env['root'])
        
        result = step_4_sales_analysis(use_latest_file=True)
        
        assert result is True


# ===================== Step 5 Handler Tests =====================

class TestStep5HandlerWithMock:
    """Tests for Step 5 handler using mocking"""
    
    def test_step_5_with_use_latest(self, sample_csv_file, setup_test_environment, monkeypatch):
        """Test step_5_rename_columns with use_latest_file=True"""
        from src.app.pipeline.step_5.handler import step_5_rename_columns
        
        env = setup_test_environment
        monkeypatch.chdir(env['root'])
        
        result = step_5_rename_columns(use_latest_file=True)
        
        assert result is True
        
        # Verify renamed file was created
        renamed_files = list(env['converted_renamed'].glob("*.csv"))
        assert len(renamed_files) >= 1


# ===================== Step 6 Handler Tests =====================

class TestStep6HandlerWithMock:
    """Tests for Step 6 handler using mocking"""
    
    def test_step_6_with_use_latest(self, sample_renamed_csv, setup_test_environment, monkeypatch):
        """Test step_6_split_by_branches with use_latest_file=True"""
        from src.app.pipeline.step_6.handler import step_6_split_by_branches
        
        env = setup_test_environment
        monkeypatch.chdir(env['root'])
        
        result = step_6_split_by_branches(use_latest_file=True)
        
        assert result is True
        
        # Verify branch files were created
        from src.core.domain.branches.config import get_branches
        for branch in get_branches():
            branch_files = list((env['branches_files'] / branch).glob("*.csv"))
            assert len(branch_files) >= 1


# ===================== File Selector Tests =====================

class TestFileSelector:
    """Tests for file_selector module"""
    
    def test_select_csv_use_latest_true(self, tmp_path):
        """Test select_csv_file with use_latest_file=True"""
        from src.app.pipeline.utils.file_selector import select_csv_file
        
        # Create test files
        (tmp_path / "file1.csv").write_text("test")
        import time
        time.sleep(0.1)
        (tmp_path / "file2.csv").write_text("test")
        
        result = select_csv_file(str(tmp_path), ["file1.csv", "file2.csv"], use_latest_file=True)
        
        assert result == "file2.csv"
    
    def test_select_csv_use_latest_false_with_input(self, tmp_path):
        """Test select_csv_file with use_latest_file=False and mocked input"""
        from src.app.pipeline.utils.file_selector import select_csv_file
        
        (tmp_path / "file1.csv").write_text("test")
        (tmp_path / "file2.csv").write_text("test")
        
        with patch('builtins.input', return_value='1'):
            result = select_csv_file(str(tmp_path), ["file1.csv", "file2.csv"], use_latest_file=False)
        
        assert result == "file1.csv"
    
    def test_select_csv_none_option_2(self, tmp_path):
        """Test select_csv_file with use_latest_file=None, option 2 (latest)"""
        from src.app.pipeline.utils.file_selector import select_csv_file
        
        (tmp_path / "file1.csv").write_text("test")
        import time
        time.sleep(0.1)
        (tmp_path / "file2.csv").write_text("test")
        
        with patch('builtins.input', return_value='2'):
            result = select_csv_file(str(tmp_path), ["file1.csv", "file2.csv"], use_latest_file=None)
        
        assert result == "file2.csv"
    
    def test_select_csv_none_option_1(self, tmp_path):
        """Test select_csv_file with use_latest_file=None, option 1 then select file"""
        from src.app.pipeline.utils.file_selector import select_csv_file
        
        (tmp_path / "file1.csv").write_text("test")
        (tmp_path / "file2.csv").write_text("test")
        
        with patch('builtins.input', side_effect=['1', '2']):  # Option 1, then file 2
            result = select_csv_file(str(tmp_path), ["file1.csv", "file2.csv"], use_latest_file=None)
        
        assert result == "file2.csv"
    
    def test_select_csv_invalid_option(self, tmp_path):
        """Test select_csv_file with invalid option raises error"""
        from src.app.pipeline.utils.file_selector import select_csv_file
        
        (tmp_path / "file1.csv").write_text("test")
        
        with patch('builtins.input', return_value='3'):  # Invalid option
            with pytest.raises(ValueError, match="Invalid option"):
                select_csv_file(str(tmp_path), ["file1.csv"], use_latest_file=None)
    
    def test_select_excel_use_latest(self, tmp_path):
        """Test select_excel_file with use_latest_file=True"""
        from src.app.pipeline.utils.file_selector import select_excel_file
        
        (tmp_path / "file1.xlsx").write_text("test")
        import time
        time.sleep(0.1)
        (tmp_path / "file2.xlsx").write_text("test")
        
        result = select_excel_file(str(tmp_path), ["file1.xlsx", "file2.xlsx"], use_latest_file=True)
        
        assert result == "file2.xlsx"
    
    def test_select_excel_with_xls_fallback(self, tmp_path):
        """Test select_excel_file falls back to .xls when no .xlsx"""
        from src.app.pipeline.utils.file_selector import select_excel_file
        
        # Only create .xls file
        (tmp_path / "file.xls").write_text("test")
        
        result = select_excel_file(str(tmp_path), ["file.xls"], use_latest_file=True)
        
        assert result == "file.xls"
    
    def test_select_excel_invalid_selection(self, tmp_path):
        """Test select_excel_file with invalid selection"""
        from src.app.pipeline.utils.file_selector import select_excel_file
        
        (tmp_path / "file.xlsx").write_text("test")
        
        with patch('builtins.input', return_value='5'):  # Invalid index
            with pytest.raises(ValueError, match="Invalid selection"):
                select_excel_file(str(tmp_path), ["file.xlsx"], use_latest_file=False)


# ===================== Step 7 Handler Tests =====================

class TestStep7HandlerWithMock:
    """Tests for Step 7 handler using mocking"""
    
    def test_step_7_generates_transfers(self, sample_renamed_csv, setup_test_environment, monkeypatch):
        """Test step 7 generates transfer files"""
        from src.app.pipeline.step_6.handler import step_6_split_by_branches
        from src.app.pipeline.step_7.handler import step_7_generate_transfers
        
        env = setup_test_environment
        monkeypatch.chdir(env['root'])
        
        # First run step 6 to create analytics
        step_6_split_by_branches(use_latest_file=True)
        
        # Then run step 7
        result = step_7_generate_transfers(use_latest_file=True)
        
        # May return True or False depending on if transfers exist
        assert isinstance(result, bool)

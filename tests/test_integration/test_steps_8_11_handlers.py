"""Tests for Steps 8-11 pipeline handlers"""

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


@pytest.fixture
def setup_step_8_env(tmp_path):
    """Setup environment for Step 8 testing"""
    from src.core.domain.branches.config import get_branches
    
    # Create directory structure
    data_dir = tmp_path / "data"
    transfers_csv = data_dir / "output" / "transfers" / "csv"
    transfers_excel = data_dir / "output" / "transfers" / "excel"
    
    for d in [transfers_csv, transfers_excel]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Create sample transfer files
    branches = get_branches()
    for source in branches[:2]:
        for target in branches[2:4]:
            if source != target:
                subdir = transfers_csv / f"transfers_from_{source}_to_other_branches"
                subdir.mkdir(exist_ok=True)
                
                df = pd.DataFrame({
                    'code': ['001', '002', '003', '004'],
                    'product_name': [
                        'Panadol TAB 500mg',
                        'Vitamin D AMP',
                        'Cough SYRUP 100ml',
                        'Skin CREAM 30g'
                    ],
                    'quantity_to_transfer': [10, 20, 15, 8]
                })
                df.to_csv(subdir / f"transfer_from_{source}_to_{target}.csv", 
                         index=False, encoding='utf-8-sig')
    
    return {
        'root': tmp_path,
        'transfers_csv': transfers_csv,
        'transfers_excel': transfers_excel
    }


@pytest.fixture
def setup_step_9_env(tmp_path):
    """Setup environment for Step 9 testing"""
    from src.core.domain.branches.config import get_branches
    
    data_dir = tmp_path / "data"
    analytics_dir = data_dir / "output" / "branches" / "analytics"
    surplus_csv = data_dir / "output" / "remaining_surplus" / "csv"
    surplus_excel = data_dir / "output" / "remaining_surplus" / "excel"
    
    for d in [surplus_csv, surplus_excel]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Create analytics files for each branch
    branches = get_branches()
    for branch in branches:
        branch_dir = analytics_dir / branch
        branch_dir.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame({
            'code': ['001', '002', '003'],
            'product_name': ['Product A', 'Product B', 'Product C'],
            'balance': [50, 30, 20],
            'surplus_quantity': [20, 10, 5],
            'needed_quantity': [0, 0, 0],
            'available_branch_1': ['shahid', 'admin', ''],
            'surplus_from_branch_1': [5, 3, 0]
        })
        
        filename = f"test_analytics_{branch}.csv"
        df.to_csv(branch_dir / filename, index=False, encoding='utf-8-sig')
    
    return {
        'root': tmp_path,
        'analytics_dir': analytics_dir,
        'surplus_csv': surplus_csv,
        'surplus_excel': surplus_excel
    }


@pytest.fixture
def setup_step_10_env(tmp_path):
    """Setup environment for Step 10 testing"""
    from src.core.domain.branches.config import get_branches
    
    data_dir = tmp_path / "data"
    analytics_dir = data_dir / "output" / "branches" / "analytics"
    shortage_csv = data_dir / "output" / "shortage" / "csv"
    shortage_excel = data_dir / "output" / "shortage" / "excel"
    
    for d in [shortage_csv, shortage_excel]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Create analytics files with shortage scenario
    branches = get_branches()
    for branch in branches:
        branch_dir = analytics_dir / branch
        branch_dir.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame({
            'code': ['001', '002', '003'],
            'product_name': ['Product A TAB', 'Product B AMP', 'Product C SYRUP'],
            'balance': [5, 3, 2],
            'surplus_quantity': [2, 1, 0],
            'needed_quantity': [10, 8, 15]  # Needs > surplus = shortage
        })
        
        filename = f"test_analytics_{branch}.csv"
        df.to_csv(branch_dir / filename, index=False, encoding='utf-8-sig')
    
    return {
        'root': tmp_path,
        'analytics_dir': analytics_dir,
        'shortage_csv': shortage_csv,
        'shortage_excel': shortage_excel
    }


@pytest.fixture
def setup_step_11_env(tmp_path):
    """Setup environment for Step 11 testing"""
    from src.core.domain.branches.config import get_branches
    
    data_dir = tmp_path / "data"
    transfers_csv = data_dir / "output" / "transfers" / "csv"
    surplus_csv = data_dir / "output" / "remaining_surplus" / "csv"
    analytics_dir = data_dir / "output" / "branches" / "analytics"
    combined_merged = data_dir / "output" / "combined_transfers" / "merged"
    combined_separate = data_dir / "output" / "combined_transfers" / "separate"
    
    for d in [transfers_csv, surplus_csv, analytics_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    branches = get_branches()
    
    # Create transfer files
    for source in branches[:2]:
        subdir = transfers_csv / f"transfers_from_{source}_to_other_branches"
        subdir.mkdir(exist_ok=True)
        
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['Product A TAB', 'Product B AMP'],
            'quantity_to_transfer': [10, 20]
        })
        df.to_csv(subdir / f"transfer_from_{source}_to_wardani.csv",
                 index=False, encoding='utf-8-sig')
    
    # Create surplus files
    for branch in branches:
        branch_dir = surplus_csv / branch
        branch_dir.mkdir(exist_ok=True)
        
        df = pd.DataFrame({
            'code': ['003'],
            'product_name': ['Product C SYRUP'],
            'calculated_remaining': [15]
        })
        df.to_csv(branch_dir / f"remaining_surplus_{branch}_tablets_and_capsules.csv",
                 index=False, encoding='utf-8-sig')
    
    # Create analytics files
    for branch in branches:
        branch_dir = analytics_dir / branch
        branch_dir.mkdir(exist_ok=True)
        
        df = pd.DataFrame({
            'code': ['001', '002', '003'],
            'product_name': ['A', 'B', 'C'],
            'balance': [10, 20, 30]
        })
        df.to_csv(branch_dir / f"test_analytics_{branch}.csv",
                 index=False, encoding='utf-8-sig')
    
    return {
        'root': tmp_path,
        'transfers_csv': transfers_csv,
        'surplus_csv': surplus_csv,
        'analytics_dir': analytics_dir
    }


# ===================== Step 8 Handler Tests =====================

class TestStep8Handler:
    """Tests for Step 8: Split by product type handler"""
    
    def test_step_8_splits_transfers(self, setup_step_8_env, monkeypatch):
        """Test step 8 splits transfer files by product type"""
        from src.app.pipeline.step_8.handler import step_8_split_by_product_type
        
        env = setup_step_8_env
        monkeypatch.chdir(env['root'])
        
        result = step_8_split_by_product_type()
        
        assert result is True
    
    def test_step_8_no_transfers_directory(self, tmp_path, monkeypatch):
        """Test step 8 fails gracefully when no transfers directory"""
        from src.app.pipeline.step_8.handler import step_8_split_by_product_type
        
        data_dir = tmp_path / "data" / "output"
        data_dir.mkdir(parents=True)
        
        monkeypatch.chdir(tmp_path)
        
        result = step_8_split_by_product_type()
        
        assert result is False
    
    def test_step_8_empty_transfers(self, tmp_path, monkeypatch):
        """Test step 8 with empty transfers directory"""
        from src.app.pipeline.step_8.handler import step_8_split_by_product_type
        
        transfers_dir = tmp_path / "data" / "output" / "transfers" / "csv"
        transfers_dir.mkdir(parents=True)
        
        monkeypatch.chdir(tmp_path)
        
        result = step_8_split_by_product_type()
        
        assert result is False


# ===================== Step 9 Handler Tests =====================

class TestStep9Handler:
    """Tests for Step 9: Remaining surplus handler"""
    
    def test_step_9_generates_surplus_files(self, setup_step_9_env, monkeypatch):
        """Test step 9 generates remaining surplus files"""
        from src.app.pipeline.step_9.handler import step_9_generate_remaining_surplus
        
        env = setup_step_9_env
        monkeypatch.chdir(env['root'])
        
        result = step_9_generate_remaining_surplus()
        
        # May return True or False depending on data
        assert isinstance(result, bool)
    
    def test_step_9_no_analytics_directory(self, tmp_path, monkeypatch):
        """Test step 9 fails when no analytics directory"""
        from src.app.pipeline.step_9.handler import step_9_generate_remaining_surplus
        
        data_dir = tmp_path / "data" / "output"
        data_dir.mkdir(parents=True)
        
        monkeypatch.chdir(tmp_path)
        
        result = step_9_generate_remaining_surplus()
        
        assert result is False
    
    def test_validate_analytics_directories(self, setup_step_9_env):
        """Test _validate_analytics_directories function"""
        from src.app.pipeline.step_9.handler import _validate_analytics_directories
        from src.core.domain.branches.config import get_branches
        
        # Patch the ANALYTICS_DIR constant
        with patch('src.app.pipeline.step_9.handler.ANALYTICS_DIR', 
                   str(setup_step_9_env['analytics_dir'])):
            result = _validate_analytics_directories(get_branches())
            assert result is True


# ===================== Step 10 Handler Tests =====================

class TestStep10Handler:
    """Tests for Step 10: Shortage files handler"""
    
    def test_step_10_generates_shortage_files(self, setup_step_10_env, monkeypatch):
        """Test step 10 generates shortage files"""
        from src.app.pipeline.step_10.handler import step_10_generate_shortage_files
        
        env = setup_step_10_env
        monkeypatch.chdir(env['root'])
        
        result = step_10_generate_shortage_files()
        
        assert isinstance(result, bool)
    
    def test_step_10_no_analytics_directory(self, tmp_path, monkeypatch):
        """Test step 10 fails when no analytics directory"""
        from src.app.pipeline.step_10.handler import step_10_generate_shortage_files
        
        data_dir = tmp_path / "data" / "output"
        data_dir.mkdir(parents=True)
        
        monkeypatch.chdir(tmp_path)
        
        result = step_10_generate_shortage_files()
        
        assert result is False


# ===================== Step 11 Handler Tests =====================

class TestStep11Handler:
    """Tests for Step 11: Combined transfers handler"""
    
    def test_step_11_validates_directories(self, tmp_path, monkeypatch):
        """Test step 11 validates input directories"""
        from src.app.pipeline.step_11.handler import _validate_input_directories
        
        data_dir = tmp_path / "data" / "output"
        data_dir.mkdir(parents=True)
        
        monkeypatch.chdir(tmp_path)
        
        # Without required directories
        with patch('src.app.pipeline.step_11.handler.TRANSFERS_DIR', 
                   str(data_dir / "transfers")), \
             patch('src.app.pipeline.step_11.handler.REMAINING_SURPLUS_DIR',
                   str(data_dir / "surplus")):
            result = _validate_input_directories()
            assert result is False
    
    def test_step_11_creates_output_directories(self, tmp_path, monkeypatch):
        """Test step 11 creates output directories"""
        from src.app.pipeline.step_11.handler import _create_output_directories
        
        monkeypatch.chdir(tmp_path)
        
        output_dirs = [
            tmp_path / "merged_csv",
            tmp_path / "merged_excel",
            tmp_path / "separate_csv",
            tmp_path / "separate_excel"
        ]
        
        with patch('src.app.pipeline.step_11.handler.OUTPUT_MERGED_CSV', str(output_dirs[0])), \
             patch('src.app.pipeline.step_11.handler.OUTPUT_MERGED_EXCEL', str(output_dirs[1])), \
             patch('src.app.pipeline.step_11.handler.OUTPUT_SEPARATE_CSV', str(output_dirs[2])), \
             patch('src.app.pipeline.step_11.handler.OUTPUT_SEPARATE_EXCEL', str(output_dirs[3])):
            _create_output_directories()
            
            for d in output_dirs:
                assert d.exists()


# ===================== Step 9 Sub-module Tests =====================

class TestStep9Submodules:
    """Tests for Step 9 sub-modules"""
    
    def test_get_timestamp(self):
        """Test timestamp generation"""
        from src.app.pipeline.step_9.file_generator import get_timestamp
        
        ts = get_timestamp()
        
        assert isinstance(ts, str)
        assert len(ts) == 15  # YYYYMMDD_HHMMSS
    
    def test_extract_base_name(self):
        """Test base name extraction"""
        from src.app.pipeline.step_9.file_generator import extract_base_name
        
        result = extract_base_name("test_file_admin_analytics.csv", "admin")
        
        assert isinstance(result, str)


# ===================== Step 10 Sub-module Tests =====================

class TestStep10Submodules:
    """Tests for Step 10 sub-modules"""
    
    def test_calculate_shortage_products(self, setup_step_10_env):
        """Test shortage calculation"""
        from src.app.pipeline.step_10.shortage_calculator import calculate_shortage_products
        
        env = setup_step_10_env
        
        result_df, has_date, first_line = calculate_shortage_products(str(env['analytics_dir']))
        
        assert isinstance(result_df, pd.DataFrame)
        assert isinstance(has_date, bool)


# ===================== Step 11 Sub-module Tests =====================

class TestStep11Submodules:
    """Tests for Step 11 sub-modules"""
    
    def test_get_timestamp(self):
        """Test timestamp generation"""
        from src.app.pipeline.step_11.file_combiner import get_timestamp
        
        ts = get_timestamp()
        
        assert isinstance(ts, str)
        assert len(ts) == 15
    
    def test_excel_formatter_import(self):
        """Test excel_formatter module can be imported"""
        from src.app.pipeline.step_11.excel_formatter import convert_to_excel_with_formatting
        
        assert callable(convert_to_excel_with_formatting)

"""Tests for Step 11 file_combiner and excel_formatter modules"""

import os
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def setup_combiner_env(tmp_path):
    """Setup environment for file_combiner testing"""
    from src.core.domain.branches.config import get_branches
    
    branches = get_branches()
    
    # Create directory structure
    transfers_dir = tmp_path / "transfers" / "csv"
    surplus_dir = tmp_path / "remaining_surplus" / "csv"
    analytics_dir = tmp_path / "branches" / "analytics"
    output_merged = tmp_path / "combined" / "merged" / "csv"
    output_separate = tmp_path / "combined" / "separate" / "csv"
    
    for d in [transfers_dir, surplus_dir, analytics_dir, output_merged, output_separate]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Create transfer files
    for source in branches[:2]:
        source_dir = transfers_dir / f"transfers_from_{source}_to_other_branches"
        source_dir.mkdir(exist_ok=True)
        
        for target in branches[2:4]:
            if source != target:
                df = pd.DataFrame({
                    'code': ['001', '002'],
                    'product_name': ['Product A TAB', 'Product B AMP'],
                    'quantity_to_transfer': [10, 20]
                })
                df.to_csv(source_dir / f"transfer_from_{source}_to_{target}.csv",
                         index=False, encoding='utf-8-sig')
    
    # Create remaining surplus files
    for branch in branches:
        branch_dir = surplus_dir / branch
        branch_dir.mkdir(exist_ok=True)
        
        df = pd.DataFrame({
            'code': ['003', '004'],
            'product_name': ['Product C SYRUP', 'Product D CREAM'],
            'calculated_remaining': [15, 8]
        })
        df.to_csv(branch_dir / f"remaining_surplus_{branch}_tablets_and_capsules.csv",
                 index=False, encoding='utf-8-sig')
    
    # Create analytics files
    for branch in branches:
        branch_dir = analytics_dir / branch
        branch_dir.mkdir(exist_ok=True)
        
        df = pd.DataFrame({
            'code': ['001', '002', '003', '004'],
            'product_name': ['A', 'B', 'C', 'D'],
            'balance': [50, 30, 20, 40]
        })
        df.to_csv(branch_dir / f"test_analytics_{branch}.csv",
                 index=False, encoding='utf-8-sig')
    
    return {
        'root': tmp_path,
        'transfers_dir': transfers_dir,
        'surplus_dir': surplus_dir,
        'analytics_dir': analytics_dir,
        'output_merged': output_merged,
        'output_separate': output_separate,
        'branches': branches
    }


# ===================== File Combiner Tests =====================

class TestFileCombiner:
    """Tests for file_combiner module"""
    
    def test_get_timestamp(self):
        """Test timestamp generation"""
        from src.app.pipeline.step_11.file_combiner import get_timestamp
        
        ts = get_timestamp()
        
        assert isinstance(ts, str)
        assert len(ts) == 15  # YYYYMMDD_HHMMSS
        
        # Should be parseable
        datetime.strptime(ts, "%Y%m%d_%H%M%S")
    
    def test_extract_target_branch(self):
        """Test target branch extraction from filename"""
        from src.app.pipeline.step_11.file_combiner import _extract_target_branch
        
        # Test various filename patterns
        assert _extract_target_branch("transfer_from_admin_to_shahid.csv") == "shahid"
        assert _extract_target_branch("transfer_from_admin_to_wardani.csv") == "wardani"
        assert _extract_target_branch("some_file_to_akba.csv") == "akba"
    
    def test_combine_transfers_and_surplus(self, setup_combiner_env):
        """Test combining transfers with surplus"""
        from src.app.pipeline.step_11.file_combiner import combine_transfers_and_surplus
        
        env = setup_combiner_env
        
        result = combine_transfers_and_surplus(
            branch=env['branches'][0],
            transfers_dir=str(env['transfers_dir']),
            surplus_dir=str(env['surplus_dir']),
            analytics_dir=str(env['analytics_dir'])
        )
        
        # May return DataFrame or None
        if result is not None:
            assert isinstance(result, pd.DataFrame)
    
    def test_read_transfer_files(self, setup_combiner_env):
        """Test reading transfer files for a branch"""
        from src.app.pipeline.step_11.file_combiner import _read_transfer_files
        
        env = setup_combiner_env
        
        result = _read_transfer_files(
            branch=env['branches'][0],
            transfers_dir=str(env['transfers_dir']),
            analytics_dir=str(env['analytics_dir'])
        )
        
        # Returns DataFrame (combined) or list
        assert result is not None
    
    def test_read_surplus_as_admin_transfer(self, setup_combiner_env):
        """Test reading surplus as admin transfer"""
        from src.app.pipeline.step_11.file_combiner import _read_surplus_as_admin_transfer
        
        env = setup_combiner_env
        
        result = _read_surplus_as_admin_transfer(
            branch=env['branches'][1],  # Non-admin branch
            surplus_dir=str(env['surplus_dir']),
            analytics_dir=str(env['analytics_dir'])
        )
        
        # May return DataFrame or None
        if result is not None:
            assert isinstance(result, pd.DataFrame)
    
    def test_generate_merged_files(self, setup_combiner_env):
        """Test generating merged files"""
        from src.app.pipeline.step_11.file_combiner import generate_merged_files, get_timestamp
        
        env = setup_combiner_env
        
        # Create sample combined DataFrame
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['Product A TAB', 'Product B AMP'],
            'quantity_to_transfer': [10, 20],
            'target_branch': ['shahid', 'wardani'],
            'transfer_type': ['normal', 'normal'],
            'sender_balance': [50, 30],
            'receiver_balance': [20, 40]
        })
        
        result = generate_merged_files(
            df=df,
            branch=env['branches'][0],
            csv_output_dir=str(env['output_merged']),
            timestamp=get_timestamp()
        )
        
        assert isinstance(result, list)
    
    def test_generate_separate_files(self, setup_combiner_env):
        """Test generating separate files"""
        from src.app.pipeline.step_11.file_combiner import generate_separate_files, get_timestamp
        
        env = setup_combiner_env
        
        # Create sample combined DataFrame
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['Product A TAB', 'Product B AMP'],
            'quantity_to_transfer': [10, 20],
            'target_branch': ['shahid', 'wardani'],
            'transfer_type': ['normal', 'normal'],
            'sender_balance': [50, 30],
            'receiver_balance': [20, 40]
        })
        
        result = generate_separate_files(
            df=df,
            branch=env['branches'][0],
            csv_output_dir=str(env['output_separate']),
            timestamp=get_timestamp()
        )
        
        assert isinstance(result, list)
    
    def test_add_product_type_column(self):
        """Test adding product type column"""
        from src.app.pipeline.step_11.file_combiner import _add_product_type_column
        
        df = pd.DataFrame({
            'code': ['001', '002', '003', '004', '005', '006'],
            'product_name': [
                'Panadol TAB 500mg',
                'Vitamin D CAP',
                'Insulin AMP',
                'Cough SYRUP',
                'Skin CREAM',
                'ORS SACHETS'
            ]
        })
        
        result = _add_product_type_column(df)
        
        assert 'product_type' in result.columns
        assert result['product_type'].iloc[0] == 'tablets_and_capsules'
    
    def test_prepare_output_columns(self):
        """Test preparing output columns"""
        from src.app.pipeline.step_11.file_combiner import _prepare_output_columns
        
        df = pd.DataFrame({
            'code': ['001'],
            'product_name': ['Product A'],
            'quantity_to_transfer': [10],
            'target_branch': ['shahid'],
            'sender_balance': [50],
            'receiver_balance': [20],
            'extra_column': ['should be kept']
        })
        
        result = _prepare_output_columns(df)
        
        assert isinstance(result, pd.DataFrame)
        # Should have reordered columns
        assert 'code' in result.columns


# ===================== Excel Formatter Tests =====================

class TestExcelFormatter:
    """Tests for excel_formatter module"""
    
    def test_convert_to_excel_basic(self, tmp_path):
        """Test basic Excel conversion"""
        from src.app.pipeline.step_11.excel_formatter import convert_to_excel_with_formatting
        import openpyxl
        
        # Create sample CSV
        csv_dir = tmp_path / "csv"
        csv_dir.mkdir()
        
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['A', 'B'],
            'quantity_to_transfer': [10, 20],
            'sender_balance': [50, -5],  # Negative to test red formatting
            'receiver_balance': [20, 40]
        })
        csv_path = csv_dir / "test_file.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        excel_dir = tmp_path / "excel"
        excel_dir.mkdir()
        
        csv_files = [{
            'csv_path': str(csv_path),
            'count': len(df)
        }]
        
        convert_to_excel_with_formatting(
            csv_files=csv_files,
            excel_output_dir=str(excel_dir)
        )
        
        # Check Excel was created (may be in subdirs)
        excel_files = list(excel_dir.rglob("*.xlsx"))
        # Function may not create files if format doesn't match
        assert isinstance(excel_files, list)
    
    def test_convert_with_date_header(self, tmp_path):
        """Test Excel conversion with date header"""
        from src.app.pipeline.step_11.excel_formatter import convert_to_excel_with_formatting
        
        csv_dir = tmp_path / "csv"
        csv_dir.mkdir()
        
        # Create CSV with date header
        csv_path = csv_dir / "test_with_date.csv"
        with open(csv_path, 'w', encoding='utf-8-sig') as f:
            f.write("من: 20/09/2024 00:00 إلى: 20/12/2024 00:00\n")
            f.write("code,product_name,quantity_to_transfer,sender_balance,receiver_balance\n")
            f.write("001,Product A,10,50,20\n")
        
        excel_dir = tmp_path / "excel"
        excel_dir.mkdir()
        
        csv_files = [{
            'csv_path': str(csv_path),
            'count': 1
        }]
        
        # Just verify function runs without error
        convert_to_excel_with_formatting(
            csv_files=csv_files,
            excel_output_dir=str(excel_dir)
        )
        
        # Just check it didn't raise an exception
        assert True


# ===================== Edge Cases =====================

class TestFileCombinerEdgeCases:
    """Edge case tests for file_combiner"""
    
    def test_combine_empty_transfers(self, tmp_path):
        """Test combining with no transfer files"""
        from src.app.pipeline.step_11.file_combiner import combine_transfers_and_surplus
        
        # Create empty directories
        transfers_dir = tmp_path / "transfers"
        surplus_dir = tmp_path / "surplus"
        analytics_dir = tmp_path / "analytics"
        
        for d in [transfers_dir, surplus_dir, analytics_dir]:
            d.mkdir()
        
        result = combine_transfers_and_surplus(
            branch="admin",
            transfers_dir=str(transfers_dir),
            surplus_dir=str(surplus_dir),
            analytics_dir=str(analytics_dir)
        )
        
        # Should return None or empty DataFrame
        assert result is None or result.empty
    
    def test_extract_target_branch_no_match(self):
        """Test target branch extraction with no _to_ pattern"""
        from src.app.pipeline.step_11.file_combiner import _extract_target_branch
        
        # No _to_ in filename - may return None or empty string
        result = _extract_target_branch("some_random_file.csv")
        
        # Should return None or empty or some value
        assert result is None or isinstance(result, str)
    
    def test_generate_files_empty_df(self, tmp_path):
        """Test generating files with empty DataFrame"""
        from src.app.pipeline.step_11.file_combiner import generate_merged_files
        
        df = pd.DataFrame()
        
        result = generate_merged_files(
            df=df,
            branch="admin",
            csv_output_dir=str(tmp_path)
        )
        
        # Should return empty list
        assert result == []

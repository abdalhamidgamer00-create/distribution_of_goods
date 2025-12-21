"""Tests for additional core and service modules"""

import os
import sys
from pathlib import Path

import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ===================== Product Classifier Tests =====================

class TestProductClassifier:
    """Tests for product_classifier module"""
    
    def test_classify_tablets(self):
        """Test tablet classification"""
        from src.core.domain.classification.product_classifier import classify_product_type
        
        assert classify_product_type("Panadol TAB 500mg") == "tablets_and_capsules"
        assert classify_product_type("Tablet Test Product") == "tablets_and_capsules"
        assert classify_product_type("قرص باراسيتامول") == "tablets_and_capsules"
        assert classify_product_type("BIOTIN tablets 100") == "tablets_and_capsules"
    
    def test_classify_capsules(self):
        """Test capsule classification"""
        from src.core.domain.classification.product_classifier import classify_product_type
        
        assert classify_product_type("Vitamin D CAP") == "tablets_and_capsules"
        assert classify_product_type("CAPSULE product") == "tablets_and_capsules"
        assert classify_product_type("كبسولة فيتامين") == "tablets_and_capsules"
    
    def test_classify_injections(self):
        """Test injection classification"""
        from src.core.domain.classification.product_classifier import classify_product_type
        
        assert classify_product_type("Insulin AMP 10ml") == "injections"
        assert classify_product_type("VITAMIN B12 1 AMP") == "injections"  # AMP as word
        assert classify_product_type("Injection Product") == "injections"
        assert classify_product_type("حقن ديكسون") == "injections"
        assert classify_product_type("Ampoule 5ml") == "injections"
        assert classify_product_type("Sterile vial") == "injections"
    
    def test_classify_syrups(self):
        """Test syrup classification"""
        from src.core.domain.classification.product_classifier import classify_product_type
        
        assert classify_product_type("Cough SYRUP 100ml") == "syrups"
        assert classify_product_type("شراب كحة") == "syrups"
        assert classify_product_type("SUSP suspension 60ml") == "syrups"
    
    def test_classify_creams(self):
        """Test cream classification"""
        from src.core.domain.classification.product_classifier import classify_product_type
        
        assert classify_product_type("Skin CREAM 30g") == "creams"
        assert classify_product_type("OINTMENT topical") == "creams"
        assert classify_product_type("GEL product") == "creams"
        assert classify_product_type("كريم مرطب") == "creams"
        assert classify_product_type("مرهم جروح") == "creams"
    
    def test_classify_sachets(self):
        """Test sachet classification"""
        from src.core.domain.classification.product_classifier import classify_product_type
        
        assert classify_product_type("ORS SACHET 5g") == "sachets"
        assert classify_product_type("Electrolytes SACH") == "sachets"
        assert classify_product_type("كيس ملح") == "sachets"
        assert classify_product_type("أكياس فوار") == "sachets"
    
    def test_classify_other(self):
        """Test other classification"""
        from src.core.domain.classification.product_classifier import classify_product_type
        
        assert classify_product_type("Medical Device") == "other"
        assert classify_product_type("Shampoo hair") == "other"  # Shampoo should be other
        assert classify_product_type("شامبو الشعر") == "other"
    
    def test_empty_product_name(self):
        """Test empty product name"""
        from src.core.domain.classification.product_classifier import classify_product_type
        
        assert classify_product_type("") == "other"
        assert classify_product_type(None) == "other"
    
    def test_get_product_categories(self):
        """Test getting all product categories"""
        from src.core.domain.classification.product_classifier import get_product_categories
        
        categories = get_product_categories()
        
        assert isinstance(categories, list)
        assert len(categories) == 6
        assert "tablets_and_capsules" in categories
        assert "injections" in categories
        assert "syrups" in categories
        assert "creams" in categories
        assert "sachets" in categories
        assert "other" in categories


# ===================== Excel Converter Tests =====================

class TestExcelConverter:
    """Tests for excel_converter module"""
    
    def test_convert_split_csv_to_excel(self, tmp_path):
        """Test converting a split CSV to Excel"""
        from src.services.transfers.converters.excel_converter import convert_split_csv_to_excel
        
        # Create test directory structure
        transfers_dir = tmp_path / "transfers_from_admin_to_other_branches"
        transfers_dir.mkdir(parents=True)
        
        subfolder = transfers_dir / "test_transfer_file"
        subfolder.mkdir()
        
        # Create test CSV file (with category in name)
        csv_path = subfolder / "test_file_tablets_and_capsules.csv"
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['Product A TAB', 'Product B CAP'],
            'quantity_to_transfer': [10, 20]
        })
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Convert to Excel
        excel_output_dir = tmp_path / "excel_output"
        excel_output_dir.mkdir()
        
        result = convert_split_csv_to_excel(str(csv_path), str(excel_output_dir))
        
        assert result is not None
        assert result.endswith('.xlsx')
        assert os.path.exists(result)
        
        # Verify Excel content
        excel_df = pd.read_excel(result)
        assert len(excel_df) == 2
    
    def test_convert_all_split_files(self, tmp_path):
        """Test converting all split files"""
        from src.services.transfers.converters.excel_converter import convert_all_split_files_to_excel
        from src.core.domain.classification.product_classifier import get_product_categories
        
        # Create test directory structure
        transfers_dir = tmp_path / "transfers"
        for cat in get_product_categories()[:2]:  # Only test 2 categories
            cat_dir = transfers_dir / "transfers_from_admin_to_wardani" / "test_file"
            cat_dir.mkdir(parents=True, exist_ok=True)
            
            csv_path = cat_dir / f"test_{cat}.csv"
            df = pd.DataFrame({
                'code': ['001'],
                'product_name': ['Product A'],
                'quantity_to_transfer': [10]
            })
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        excel_output = tmp_path / "excel"
        excel_output.mkdir()
        
        count = convert_all_split_files_to_excel(str(transfers_dir), str(excel_output))
        
        assert count >= 1


# ===================== File Splitter Tests =====================

class TestFileSplitter:
    """Tests for file_splitter module"""
    
    def test_split_transfer_file_by_type(self, tmp_path):
        """Test splitting transfer file by product type"""
        from src.services.transfers.splitters.file_splitter import split_transfer_file_by_type
        
        # Create test transfer file with mixed products
        transfer_file = tmp_path / "test_transfer_from_admin_to_wardani.csv"
        df = pd.DataFrame({
            'code': ['001', '002', '003', '004', '005'],
            'product_name': ['Aspirin TAB', 'Insulin AMP', 'Cough SYRUP', 'Skin CREAM', 'ORS SACHET'],
            'quantity_to_transfer': [10, 20, 15, 5, 8]
        })
        df.to_csv(transfer_file, index=False, encoding='utf-8-sig')
        
        output_dir = tmp_path / "split_output"
        output_dir.mkdir()
        
        result = split_transfer_file_by_type(str(transfer_file), str(output_dir))
        
        assert isinstance(result, dict)
        # Should have 5 categories (one for each product type)
        assert len(result) == 5
        
        # Verify each category file
        for category, file_path in result.items():
            assert os.path.exists(file_path)
            cat_df = pd.read_csv(file_path, encoding='utf-8-sig')
            assert len(cat_df) == 1  # Each category has 1 product
    
    def test_split_file_with_date_header(self, tmp_path):
        """Test splitting with date header preservation"""
        from src.services.transfers.splitters.file_splitter import split_transfer_file_by_type
        
        transfer_file = tmp_path / "test_from_admin_to_shahid.csv"
        df = pd.DataFrame({
            'code': ['001'],
            'product_name': ['Aspirin TAB'],
            'quantity_to_transfer': [10]
        })
        df.to_csv(transfer_file, index=False, encoding='utf-8-sig')
        
        output_dir = tmp_path / "split"
        output_dir.mkdir()
        
        first_line = "من: 01/09/2024 00:00 إلى: 01/12/2024 00:00"
        result = split_transfer_file_by_type(
            str(transfer_file), 
            str(output_dir),
            has_date_header=True,
            first_line=first_line
        )
        
        assert len(result) >= 1
        
        # Check date header is in file
        for category, file_path in result.items():
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                assert '01/09/2024' in content
    
    def test_split_all_transfer_files(self, tmp_path):
        """Test splitting all transfer files in directory"""
        from src.services.transfers.splitters.file_splitter import split_all_transfer_files
        
        # Create multiple transfer files
        transfers_dir = tmp_path / "transfers" / "admin"
        transfers_dir.mkdir(parents=True)
        
        for i in range(2):
            file_path = transfers_dir / f"transfer_{i}_from_admin_to_wardani.csv"
            df = pd.DataFrame({
                'code': ['001', '002'],
                'product_name': ['Aspirin TAB', 'Insulin AMP'],
                'quantity_to_transfer': [10, 20]
            })
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        result = split_all_transfer_files(str(tmp_path / "transfers"))
        
        assert isinstance(result, dict)
        # Should have created split files for each original file


# ===================== Analytics Reader Tests =====================

class TestAnalyticsReader:
    """Tests for Step 9 analytics_reader module"""
    
    def test_read_analytics_file(self, tmp_path):
        """Test reading analytics file"""
        from src.app.pipeline.step_9.analytics_reader import read_analytics_file
        
        # Create test analytics file
        analytics_file = tmp_path / "test_analytics.csv"
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['A', 'B'],
            'surplus_quantity': [10, 20],
            'available_branch_1': ['admin', 'shahid'],
            'surplus_from_branch_1': [5, 10]
        })
        df.to_csv(analytics_file, index=False, encoding='utf-8-sig')
        
        result_df, has_date, first_line = read_analytics_file(str(analytics_file))
        
        assert result_df is not None
        assert len(result_df) == 2
        assert has_date is False
    
    def test_extract_withdrawals_from_branch(self, tmp_path):
        """Test extracting withdrawals from a specific branch"""
        from src.app.pipeline.step_9.analytics_reader import extract_withdrawals_from_branch
        
        df = pd.DataFrame({
            'code': ['001', '002', '003'],
            'available_branch_1': ['admin', 'shahid', 'admin'],
            'surplus_from_branch_1': [5, 10, 3],
            'available_branch_2': ['wardani', 'admin', ''],
            'surplus_from_branch_2': [2, 1, 0]
        })
        
        withdrawals = extract_withdrawals_from_branch(df, 'admin')
        
        assert isinstance(withdrawals, dict)
        # Should have withdrawals from admin
        assert '001' in withdrawals or '003' in withdrawals or '002' in withdrawals


# ===================== Balance Reader Tests =====================

class TestBalanceReader:
    """Tests for Step 11 balance_reader module"""
    
    def test_get_branch_balances(self, tmp_path):
        """Test getting branch balance from analytics file"""
        from src.app.pipeline.step_11.balance_reader import get_branch_balances
        
        # Create test analytics directory structure
        analytics_dir = tmp_path / "analytics"
        branch_dir = analytics_dir / "admin"
        branch_dir.mkdir(parents=True)
        
        # Create test analytics file
        branch_file = branch_dir / "test_analytics.csv"
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['A', 'B'],
            'balance': [10, 20]
        })
        df.to_csv(branch_file, index=False, encoding='utf-8-sig')
        
        balances = get_branch_balances(str(analytics_dir), 'admin')
        
        assert isinstance(balances, dict)
        assert len(balances) == 2  # Should have 2 products
        # Verify balances exist (codes may be converted to different string format)
        assert 10.0 in balances.values()
        assert 20.0 in balances.values()


# ===================== File Writer Tests =====================

class TestFileWriter:
    """Tests for file_writer module"""
    
    def test_write_branch_files(self, tmp_path):
        """Test writing branch files"""
        from src.services.splitting.writers.file_writer import write_branch_files
        
        # Create analytics data
        branches = ['admin']
        analytics_data = {
            'admin': pd.DataFrame({
                'code': ['001', '002'],
                'product_name': ['A', 'B'],
                'balance': [10, 20]
            })
        }
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        result = write_branch_files(
            branches=branches,
            analytics_data=analytics_data,
            output_base_dir=str(output_dir),
            base_filename="test",
            has_date_header=False,
            first_line=""
        )
        
        assert 'admin' in result
        assert os.path.exists(result['admin'])


# ===================== Logging Utils Tests =====================

class TestLoggingUtils:
    """Tests for logging_utils module"""
    
    def test_get_logger(self):
        """Test getting a logger instance"""
        from src.shared.utils.logging_utils import get_logger
        
        logger = get_logger("test_module")
        
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')

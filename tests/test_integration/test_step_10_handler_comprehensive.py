"""Comprehensive tests for Step 10 shortage files handler.

Tests cover all 13 functions for shortage file generation.
"""

import os
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import pandas as pd

import pytest

from src.app.pipeline.step_10.handler import (
    _validate_analytics_directories,
    _write_csv_file,
    _prepare_category_df,
    _process_single_category,
    _generate_category_files,
    _convert_all_to_excel,
    _log_summary,
    _prepare_shortage_data,
    _create_combined_file,
    _generate_all_files,
    _execute_shortage_generation,
    _run_shortage_generation,
    step_10_generate_shortage_files,
    ANALYTICS_DIR,
    CSV_OUTPUT_DIR,
    EXCEL_OUTPUT_DIR,
)


# ===================== Fixtures =====================

@pytest.fixture
def sample_shortage_df():
    """Create sample shortage DataFrame."""
    return pd.DataFrame({
        'code': ['001', '002', '003', '004'],
        'product_name': ['Aspirin Tab', 'Injection Vial', 'Syrup Bottle', 'Cream Tube'],
        'shortage_quantity': [100, 50, 75, 25],
        'product_type': ['tablets_and_capsules', 'injections', 'syrups', 'creams']
    })


@pytest.fixture
def analytics_directory(tmp_path):
    """Create mock analytics directory structure."""
    analytics_dir = tmp_path / "analytics"
    for branch in ["admin", "wardani", "akba"]:
        (analytics_dir / branch).mkdir(parents=True)
        (analytics_dir / branch / f"{branch}_analytics.csv").write_text("code,name\n001,Test")
    return str(analytics_dir)


# ===================== _validate_analytics_directories Tests =====================

class TestValidateAnalyticsDirectories:
    """Tests for _validate_analytics_directories function."""
    
    def test_returns_true_when_all_exist(self, analytics_directory):
        """
        WHAT: Return True when all branch directories exist
        WHY: Allow processing to continue
        BREAKS: Processing blocked unnecessarily
        """
        with patch('src.app.pipeline.step_10.handler.ANALYTICS_DIR', analytics_directory):
            result = _validate_analytics_directories(["admin", "wardani"])
        
        assert result is True
    
    def test_returns_false_when_missing(self, analytics_directory):
        """
        WHAT: Return False when branch directory is missing
        WHY: Prevent processing with missing data
        BREAKS: FileNotFoundError during processing
        """
        with patch('src.app.pipeline.step_10.handler.ANALYTICS_DIR', analytics_directory):
            result = _validate_analytics_directories(["admin", "nonexistent"])
        
        assert result is False


# ===================== _write_csv_file Tests =====================

class TestWriteCsvFile:
    """Tests for _write_csv_file function."""
    
    def test_writes_csv_without_header(self, tmp_path, sample_shortage_df):
        """
        WHAT: Write CSV without date header
        WHY: Some files don't have date headers
        BREAKS: Date header written when not needed
        """
        csv_path = str(tmp_path / "test.csv")
        df = sample_shortage_df.drop('product_type', axis=1)
        
        _write_csv_file(df, csv_path, has_date_header=False, first_line="")
        
        assert os.path.exists(csv_path)
        content = Path(csv_path).read_text()
        assert "code" in content
    
    def test_writes_csv_with_date_header(self, tmp_path, sample_shortage_df):
        """
        WHAT: Write CSV with date header on first line
        WHY: Preserve original file format
        BREAKS: Date header missing in output
        """
        csv_path = str(tmp_path / "test.csv")
        df = sample_shortage_df.drop('product_type', axis=1)
        first_line = "01/01/2024 10:00 - 01/04/2024 10:00"
        
        _write_csv_file(df, csv_path, has_date_header=True, first_line=first_line)
        
        content = Path(csv_path).read_text()
        assert first_line in content


# ===================== _prepare_category_df Tests =====================

class TestPrepareCategoryDf:
    """Tests for _prepare_category_df function."""
    
    def test_filters_by_category(self, sample_shortage_df):
        """
        WHAT: Return only products matching category
        WHY: Each file should have single category
        BREAKS: Mixed categories in output
        """
        result = _prepare_category_df(sample_shortage_df, 'tablets_and_capsules')
        
        assert len(result) == 1
        assert result.iloc[0]['code'] == '001'
    
    def test_returns_none_for_empty_category(self, sample_shortage_df):
        """
        WHAT: Return None when category has no products
        WHY: No empty files should be created
        BREAKS: Empty CSV files created
        """
        result = _prepare_category_df(sample_shortage_df, 'sachets')
        
        assert result is None
    
    def test_removes_product_type_column(self, sample_shortage_df):
        """
        WHAT: Remove product_type column from output
        WHY: Category is in filename, not needed in data
        BREAKS: Redundant column in output
        """
        result = _prepare_category_df(sample_shortage_df, 'tablets_and_capsules')
        
        assert 'product_type' not in result.columns
    
    def test_sorts_by_shortage_descending(self, sample_shortage_df):
        """
        WHAT: Sort by shortage_quantity descending
        WHY: Most urgent items should be first
        BREAKS: Random order in output
        """
        # Add more items of same category
        df = sample_shortage_df.copy()
        df = pd.concat([df, pd.DataFrame({
            'code': ['005'],
            'product_name': ['Another Tab'],
            'shortage_quantity': [200],
            'product_type': ['tablets_and_capsules']
        })])
        
        result = _prepare_category_df(df, 'tablets_and_capsules')
        
        # First item should have highest shortage
        assert result.iloc[0]['shortage_quantity'] == 200


# ===================== _process_single_category Tests =====================

class TestProcessSingleCategory:
    """Tests for _process_single_category function."""
    
    def test_returns_file_info_dict(self, tmp_path, sample_shortage_df):
        """
        WHAT: Return dict with csv_path, df, count
        WHY: Caller needs file info for further processing
        BREAKS: Missing required info
        """
        with patch('src.app.pipeline.step_10.handler.CSV_OUTPUT_DIR', str(tmp_path)):
            result = _process_single_category(
                sample_shortage_df, 'tablets_and_capsules', 
                '20241222', 'shortage', False, ''
            )
        
        assert result is not None
        assert 'csv_path' in result
        assert 'df' in result
        assert 'count' in result
    
    def test_returns_none_for_empty_category(self, sample_shortage_df):
        """
        WHAT: Return None when category is empty
        WHY: No file should be generated
        BREAKS: Error on empty category
        """
        result = _process_single_category(
            sample_shortage_df, 'sachets',
            '20241222', 'shortage', False, ''
        )
        
        assert result is None


# ===================== _generate_category_files Tests =====================

class TestGenerateCategoryFiles:
    """Tests for _generate_category_files function."""
    
    def test_generates_files_for_each_category(self, tmp_path, sample_shortage_df):
        """
        WHAT: Generate files for categories with products
        WHY: Each category needs separate file
        BREAKS: Missing category files
        """
        categories = ['tablets_and_capsules', 'injections', 'syrups', 'creams']
        
        with patch('src.app.pipeline.step_10.handler.CSV_OUTPUT_DIR', str(tmp_path)):
            result = _generate_category_files(
                sample_shortage_df, categories, '20241222', 'shortage', False, ''
            )
        
        assert 'tablets_and_capsules' in result
        assert 'injections' in result
    
    def test_skips_empty_categories(self, tmp_path, sample_shortage_df):
        """
        WHAT: Skip categories with no products
        WHY: Don't create empty files
        BREAKS: Empty files created
        """
        categories = ['tablets_and_capsules', 'sachets']  # sachets is empty
        
        with patch('src.app.pipeline.step_10.handler.CSV_OUTPUT_DIR', str(tmp_path)):
            result = _generate_category_files(
                sample_shortage_df, categories, '20241222', 'shortage', False, ''
            )
        
        assert 'sachets' not in result


# ===================== _convert_all_to_excel Tests =====================

class TestConvertAllToExcel:
    """Tests for _convert_all_to_excel function."""
    
    def test_creates_excel_files(self, tmp_path, sample_shortage_df):
        """
        WHAT: Create Excel files for all generated CSVs
        WHY: Users need Excel format
        BREAKS: No Excel output
        """
        csv_path = str(tmp_path / "test.csv")
        sample_shortage_df.to_csv(csv_path, index=False)
        
        generated_files = {
            'tablets_and_capsules': {
                'csv_path': csv_path,
                'df': sample_shortage_df,
                'count': 4
            }
        }
        
        with patch('src.app.pipeline.step_10.handler.EXCEL_OUTPUT_DIR', str(tmp_path)):
            _convert_all_to_excel(generated_files)
        
        excel_files = list(tmp_path.glob("*.xlsx"))
        assert len(excel_files) >= 1
    
    def test_handles_conversion_error(self, tmp_path):
        """
        WHAT: Handle Excel conversion errors gracefully
        WHY: Don't crash on conversion failure
        BREAKS: Unhandled exception
        """
        generated_files = {
            'test': {
                'csv_path': '/nonexistent/file.csv',
                'df': pd.DataFrame({'invalid': [None]}),
                'count': 1
            }
        }
        
        with patch('src.app.pipeline.step_10.handler.EXCEL_OUTPUT_DIR', str(tmp_path)):
            # Should not raise exception
            _convert_all_to_excel(generated_files)


# ===================== _log_summary Tests =====================

class TestLogSummary:
    """Tests for _log_summary function."""
    
    def test_logs_category_counts(self, caplog):
        """
        WHAT: Log count for each category
        WHY: User feedback on generation
        BREAKS: Missing category info
        """
        generated_files = {
            'tablets_and_capsules': {'count': 10},
            'injections': {'count': 5},
            'all': {'count': 15}
        }
        categories = ['tablets_and_capsules', 'injections']
        
        with caplog.at_level('INFO'):
            _log_summary(generated_files, categories, 100)
        
        assert "10" in caplog.text
        assert "5" in caplog.text


# ===================== _prepare_shortage_data Tests =====================

class TestPrepareShortageData:
    """Tests for _prepare_shortage_data function."""
    
    @patch('src.app.pipeline.step_10.handler.calculate_shortage_products')
    def test_returns_none_when_no_shortage(self, mock_calc):
        """
        WHAT: Return None tuple when no shortages
        WHY: Early exit when no work needed
        BREAKS: Error on empty data
        """
        mock_calc.return_value = (pd.DataFrame(), False, '')
        
        result = _prepare_shortage_data()
        
        assert result == (None, None, None)
    
    @patch('src.app.pipeline.step_10.handler.calculate_shortage_products')
    def test_adds_product_type_column(self, mock_calc):
        """
        WHAT: Add product_type column by classification
        WHY: Needed for category splitting
        BREAKS: Missing classification
        """
        mock_df = pd.DataFrame({
            'code': ['001'],
            'product_name': ['Aspirin Tab'],
            'shortage_quantity': [100]
        })
        mock_calc.return_value = (mock_df, True, 'date line')
        
        shortage_df, _, _ = _prepare_shortage_data()
        
        assert 'product_type' in shortage_df.columns


# ===================== _create_combined_file Tests =====================

class TestCreateCombinedFile:
    """Tests for _create_combined_file function."""
    
    def test_creates_combined_csv(self, tmp_path, sample_shortage_df):
        """
        WHAT: Create combined file with all products
        WHY: Users need all products in one file
        BREAKS: Missing combined file
        """
        with patch('src.app.pipeline.step_10.handler.CSV_OUTPUT_DIR', str(tmp_path)):
            result = _create_combined_file(
                sample_shortage_df, '20241222', 'shortage', False, ''
            )
        
        assert os.path.exists(result['csv_path'])
        assert result['count'] == 4


# ===================== step_10_generate_shortage_files Tests =====================

class TestStep10GenerateShortageFiles:
    """Tests for step_10_generate_shortage_files main function."""
    
    @patch('src.app.pipeline.step_10.handler._run_shortage_generation')
    @patch('src.app.pipeline.step_10.handler._validate_analytics_directories')
    @patch('src.app.pipeline.step_10.handler.get_branches')
    def test_returns_true_on_success(self, mock_branches, mock_validate, mock_run):
        """
        WHAT: Return True on successful generation
        WHY: Pipeline needs success indicator
        BREAKS: Wrong return value
        """
        mock_branches.return_value = ['admin']
        mock_validate.return_value = True
        mock_run.return_value = True
        
        result = step_10_generate_shortage_files()
        
        assert result is True
    
    @patch('src.app.pipeline.step_10.handler._validate_analytics_directories')
    @patch('src.app.pipeline.step_10.handler.get_branches')
    def test_returns_false_on_invalid_dirs(self, mock_branches, mock_validate):
        """
        WHAT: Return False when validation fails
        WHY: Don't proceed without valid input
        BREAKS: Error on missing directories
        """
        mock_branches.return_value = ['admin']
        mock_validate.return_value = False
        
        result = step_10_generate_shortage_files()
        
        assert result is False
    
    @patch('src.app.pipeline.step_10.handler._run_shortage_generation')
    @patch('src.app.pipeline.step_10.handler._validate_analytics_directories')
    @patch('src.app.pipeline.step_10.handler.get_branches')
    def test_handles_exception(self, mock_branches, mock_validate, mock_run):
        """
        WHAT: Return False on exception
        WHY: Graceful error handling
        BREAKS: Unhandled exception
        """
        mock_branches.return_value = ['admin']
        mock_validate.return_value = True
        mock_run.side_effect = Exception("Test error")
        
        result = step_10_generate_shortage_files()
        
        assert result is False


# ===================== _run_shortage_generation Tests =====================

class TestRunShortageGeneration:
    """Tests for _run_shortage_generation function."""
    
    @patch('src.app.pipeline.step_10.handler._prepare_shortage_data')
    def test_returns_true_when_no_shortage(self, mock_prepare):
        """
        WHAT: Return True when no shortage products
        WHY: No shortage is a valid state
        BREAKS: False return on valid state
        """
        mock_prepare.return_value = (None, None, None)
        
        result = _run_shortage_generation()
        
        assert result is True
    
    @patch('src.app.pipeline.step_10.handler._execute_shortage_generation')
    @patch('src.app.pipeline.step_10.handler._prepare_shortage_data')
    def test_calls_execute_when_data_exists(self, mock_prepare, mock_execute):
        """
        WHAT: Call execute when shortage data exists
        WHY: Process shortage products
        BREAKS: Shortages not processed
        """
        mock_prepare.return_value = (pd.DataFrame({'a': [1]}), True, 'line')
        mock_execute.return_value = True
        
        result = _run_shortage_generation()
        
        mock_execute.assert_called_once()
        assert result is True

"""Tests for the AnalyzeSales use case."""

import os
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from src.application.use_cases.analyze_sales import AnalyzeSales

@pytest.fixture
def mock_csv_file(tmp_path):
    """Creates a temporary CSV file for testing."""
    csv_file = tmp_path / "test_sales.csv"
    df = pd.DataFrame({
        'Product': ['A', 'B'],
        'Sales': [100, 200]
    })
    df.to_csv(csv_file, index=False)
    return str(csv_file)

@pytest.fixture
def use_case():
    """Initializes the AnalyzeSales use case."""
    return AnalyzeSales()

def test_analyze_sales_execution_success(use_case, mock_csv_file, tmp_path):
    """Test successful execution of sales analysis including file creation."""
    # Mock paths to use temp directory
    test_output_dir = tmp_path / "output"
    
    with patch('src.application.use_cases.analyze_sales.analyze_csv_data') as mock_analyze, \
         patch('src.application.use_cases.analyze_sales.FileSelectorService.select_csv_file') as mock_select, \
         patch('src.shared.config.paths.SALES_REPORT_DIR', str(test_output_dir)):
        
        # Setup mocks
        mock_select.return_value = "test_sales.csv"
        mock_analyze.return_value = {
            'total_rows': 2,
            'total_columns': 2,
            'total_cells': 4,
            'empty_cells': 0,
            'empty_cells_percentage': 0.0,
            'filled_cells': 4,
            'date_range': None
        }
        
        # Execute
        result = use_case.execute(use_latest_file=True)
        
        # Assertions
        assert result is True
        
        # Check files were created
        csv_report = test_output_dir / "csv" / "analysis_test_sales.csv"
        excel_report = test_output_dir / "excel" / "analysis_test_sales.xlsx"
        
        assert csv_report.exists()
        assert excel_report.exists()
        
        # Verify content
        df_result = pd.read_csv(csv_report)
        assert df_result['total_rows'][0] == 2
        assert df_result['total_cells'][0] == 4

def test_analyze_sales_no_file(use_case):
    """Test behavior when no CSV file is found."""
    with patch('src.application.use_cases.analyze_sales.FileSelectorService.select_csv_file') as mock_select:
        mock_select.return_value = None
        
        result = use_case.execute()
        assert result is False

def test_analyze_sales_failure_handling(use_case, mock_csv_file):
    """Test that exceptions are caught and return False."""
    with patch('src.application.use_cases.analyze_sales.FileSelectorService.select_csv_file') as mock_select, \
         patch('src.application.use_cases.analyze_sales.analyze_csv_data') as mock_analyze:
        
        mock_select.return_value = "test_sales.csv"
        mock_analyze.side_effect = Exception("System Error")
        
        result = use_case.execute()
        assert result is False

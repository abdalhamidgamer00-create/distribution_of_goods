import os
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.services.conversion.converters.excel_to_csv import convert_excel_to_csv
from src.app.pipeline.step_3 import step_3_validate_data

class TestStep2EdgeCases:
    """Edge case tests for Step 2: Excel to CSV conversion"""
    
    def test_convert_non_existent_file(self, tmp_path):
        """Test converting a file that doesn't exist"""
        input_path = str(tmp_path / "missing.xlsx")
        output_path = str(tmp_path / "out.csv")
        assert convert_excel_to_csv(input_path, output_path) is False
        
    def test_convert_invalid_format(self, tmp_path):
        """Test converting a non-Excel file with Excel extension"""
        input_path = tmp_path / "bad.xlsx"
        input_path.write_text("not an excel file")
        output_path = str(tmp_path / "out.csv")
        assert convert_excel_to_csv(str(input_path), output_path) is False
        
    def test_convert_empty_excel_with_headers(self, tmp_path):
        """Test converting an Excel file with headers but no data"""
        input_path = str(tmp_path / "empty_with_headers.xlsx")
        # Create an empty dataframe with columns
        df = pd.DataFrame(columns=["A", "B", "C"])
        df.to_excel(input_path, index=False)
        output_path = str(tmp_path / "out.csv")
        assert convert_excel_to_csv(input_path, output_path) is True
        assert os.path.exists(output_path)
        # Check if CSV has only headers
        out_df = pd.read_csv(output_path)
        assert out_df.empty
        assert list(out_df.columns) == ["A", "B", "C"]

class TestStep3EdgeCases:
    """Edge case tests for Step 3: Data Validation"""
    
    @patch('src.app.pipeline.step_3.validator.selection.select_csv_file')
    @patch('src.app.pipeline.step_3.validator.orchestrator.get_csv_files')
    def test_validate_missing_file(self, mock_files, mock_select):
        """Test validation when no CSV files are found"""
        mock_files.return_value = []
        assert step_3_validate_data(use_latest_file=True) is False

    @patch('src.app.pipeline.step_3.validator.validation.perform_validation', return_value=False)
    @patch('src.app.pipeline.step_3.validator.selection.select_csv_file', return_value="data.csv")
    @patch('src.app.pipeline.step_3.validator.orchestrator.get_csv_files', return_value=["data.csv"])
    def test_validate_invalid_columns(self, mock_files, mock_select, mock_perf):
        """Test validation fails when columns are invalid"""
        assert step_3_validate_data(use_latest_file=True) is False

    @patch('src.app.pipeline.step_3.validator.validation.perform_validation', return_value=True)
    @patch('src.app.pipeline.step_3.validator.validation.handle_post_validation', return_value=False)
    @patch('src.app.pipeline.step_3.validator.selection.select_csv_file', return_value="data.csv")
    @patch('src.app.pipeline.step_3.validator.orchestrator.get_csv_files', return_value=["data.csv"])
    def test_validate_post_validation_failure(self, mock_files, mock_select, mock_post, mock_perf):
        """Test validation fails during post-validation"""
        assert step_3_validate_data(use_latest_file=True) is False

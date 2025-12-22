"""Comprehensive tests for Step 2 (Excel to CSV) and Step 5 (Column Renaming) handlers.

Tests cover all functions for file conversion and column renaming.
"""

import os
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import pandas as pd

import pytest

# Step 2 imports
from src.app.pipeline.step_2.handler import (
    _generate_output_filename,
    _log_conversion_result,
    _perform_conversion,
    _validate_and_select,
    _try_convert_excel,
    step_2_convert_excel_to_csv,
)

# Step 5 imports
from src.app.pipeline.step_5.handler import (
    _generate_renamed_filename,
    _get_input_files,
    _execute_rename,
    _process_rename,
    step_5_rename_columns,
)


# ===================== Step 2: _generate_output_filename Tests =====================

class TestGenerateOutputFilename:
    """Tests for _generate_output_filename function."""
    
    def test_generates_csv_extension(self):
        """
        WHAT: Output should have .csv extension
        WHY: Correct file format for output
        BREAKS: Wrong file extension
        """
        result = _generate_output_filename("test_file.xlsx")
        
        assert result.endswith(".csv")
    
    def test_removes_old_timestamp(self):
        """
        WHAT: Remove existing timestamp from filename
        WHY: Avoid timestamp duplication
        BREAKS: Multiple timestamps in name
        """
        result = _generate_output_filename("data_20231201_120000.xlsx")
        
        # Should not have old timestamp
        assert "20231201_120000" not in result
    
    def test_adds_new_timestamp(self):
        """
        WHAT: Add current timestamp to filename
        WHY: Unique file naming
        BREAKS: Overwriting existing files
        """
        result = _generate_output_filename("test.xlsx")
        
        # Should have a timestamp pattern
        assert "_" in result
        assert len(result) > len("test.csv")


# ===================== Step 2: _log_conversion_result Tests =====================

class TestLogConversionResult:
    """Tests for _log_conversion_result function."""
    
    def test_logs_success(self, caplog):
        """
        WHAT: Log success message
        WHY: User confirmation
        BREAKS: No success feedback
        """
        with caplog.at_level('INFO'):
            _log_conversion_result(True, "/path/to/output")
        
        assert "successful" in caplog.text.lower()
    
    def test_logs_failure(self, caplog):
        """
        WHAT: Log error on failure
        WHY: User needs to know it failed
        BREAKS: Silent failure
        """
        with caplog.at_level('ERROR'):
            _log_conversion_result(False, "/path/to/output")
        
        assert "failed" in caplog.text.lower()


# ===================== Step 2: _validate_and_select Tests =====================

class TestValidateAndSelect:
    """Tests for _validate_and_select function."""
    
    @patch('src.app.pipeline.step_2.handler._select_excel_file_source')
    @patch('src.app.pipeline.step_2.handler.get_excel_files')
    def test_returns_selected_file(self, mock_files, mock_select, tmp_path):
        """
        WHAT: Return selected Excel file
        WHY: File selection for conversion
        BREAKS: No file returned
        """
        mock_files.return_value = ["file.xlsx"]
        mock_select.return_value = "file.xlsx"
        
        result = _validate_and_select(str(tmp_path), True)
        
        assert result == "file.xlsx"
    
    @patch('src.app.pipeline.step_2.handler.get_excel_files')
    def test_returns_none_when_no_files(self, mock_files, tmp_path):
        """
        WHAT: Return None when no Excel files
        WHY: Can't proceed without input
        BREAKS: Error on empty directory
        """
        mock_files.return_value = []
        
        result = _validate_and_select(str(tmp_path), True)
        
        assert result is None


# ===================== Step 2: step_2_convert_excel_to_csv Tests =====================

class TestStep2ConvertExcelToCsv:
    """Tests for step_2_convert_excel_to_csv main function."""
    
    @patch('src.app.pipeline.step_2.handler._try_convert_excel')
    @patch('src.app.pipeline.step_2.handler.ensure_directory_exists')
    def test_returns_true_on_success(self, mock_ensure, mock_convert):
        """
        WHAT: Return True on successful conversion
        WHY: Pipeline success indicator
        BREAKS: Wrong return value
        """
        mock_convert.return_value = True
        
        result = step_2_convert_excel_to_csv()
        
        assert result is True
    
    @patch('src.app.pipeline.step_2.handler._try_convert_excel')
    @patch('src.app.pipeline.step_2.handler.ensure_directory_exists')
    def test_handles_exception(self, mock_ensure, mock_convert):
        """
        WHAT: Return False on exception
        WHY: Graceful error handling
        BREAKS: Unhandled exception
        """
        mock_convert.side_effect = Exception("Error")
        
        result = step_2_convert_excel_to_csv()
        
        assert result is False


# ===================== Step 5: _generate_renamed_filename Tests =====================

class TestGenerateRenamedFilename:
    """Tests for _generate_renamed_filename function."""
    
    def test_adds_renamed_suffix(self):
        """
        WHAT: Add 'renamed' to filename
        WHY: Distinguish from original
        BREAKS: Overwriting original
        """
        result = _generate_renamed_filename("data.csv")
        
        assert "renamed" in result
    
    def test_adds_timestamp(self):
        """
        WHAT: Add timestamp to filename
        WHY: Unique file naming
        BREAKS: Overwriting files
        """
        result = _generate_renamed_filename("test.csv")
        
        # Should have timestamp pattern
        assert "_" in result
    
    def test_removes_old_timestamp(self):
        """
        WHAT: Remove existing timestamp
        WHY: Avoid timestamp duplication
        BREAKS: Multiple timestamps
        """
        result = _generate_renamed_filename("data_20231201_120000.csv")
        
        assert "20231201_120000" not in result


# ===================== Step 5: _get_input_files Tests =====================

class TestGetInputFiles:
    """Tests for _get_input_files function."""
    
    @patch('src.app.pipeline.step_5.handler.get_csv_files')
    def test_returns_files_when_exist(self, mock_files):
        """
        WHAT: Return list of CSV files
        WHY: Provide files for rename
        BREAKS: Empty list returned
        """
        mock_files.return_value = ["file1.csv", "file2.csv"]
        
        result = _get_input_files("/some/path")
        
        assert len(result) == 2
    
    @patch('src.app.pipeline.step_5.handler.get_csv_files')
    def test_returns_none_when_empty(self, mock_files):
        """
        WHAT: Return None when no files
        WHY: Early exit when no work
        BREAKS: Error on empty directory
        """
        mock_files.return_value = []
        
        result = _get_input_files("/some/path")
        
        assert result is None


# ===================== Step 5: _process_rename Tests =====================

class TestProcessRename:
    """Tests for _process_rename function."""
    
    @patch('src.app.pipeline.step_5.handler._execute_rename')
    @patch('src.app.pipeline.step_5.handler.get_file_path')
    @patch('src.app.pipeline.step_5.handler.select_csv_file')
    def test_calls_execute_rename(self, mock_select, mock_path, mock_execute, tmp_path):
        """
        WHAT: Call execute_rename with correct args
        WHY: Rename should be performed
        BREAKS: Rename never happens
        """
        mock_select.return_value = "file.csv"
        mock_path.return_value = str(tmp_path / "file.csv")
        mock_execute.return_value = True
        
        result = _process_rename(str(tmp_path), ["file.csv"], str(tmp_path), True)
        
        mock_execute.assert_called_once()
    
    @patch('src.app.pipeline.step_5.handler.select_csv_file')
    def test_handles_value_error(self, mock_select, tmp_path):
        """
        WHAT: Handle ValueError gracefully
        WHY: Invalid selection shouldn't crash
        BREAKS: Unhandled error
        """
        mock_select.side_effect = ValueError("Invalid")
        
        result = _process_rename(str(tmp_path), ["file.csv"], str(tmp_path), True)
        
        assert result is False
    
    @patch('src.app.pipeline.step_5.handler.select_csv_file')
    def test_handles_general_exception(self, mock_select, tmp_path):
        """
        WHAT: Handle general exceptions
        WHY: Graceful error handling
        BREAKS: Unhandled exception
        """
        mock_select.side_effect = Exception("Error")
        
        result = _process_rename(str(tmp_path), ["file.csv"], str(tmp_path), True)
        
        assert result is False


# ===================== Step 5: step_5_rename_columns Tests =====================

class TestStep5RenameColumns:
    """Tests for step_5_rename_columns main function."""
    
    @patch('src.app.pipeline.step_5.handler._process_rename')
    @patch('src.app.pipeline.step_5.handler._get_input_files')
    @patch('src.app.pipeline.step_5.handler.ensure_directory_exists')
    def test_returns_true_on_success(self, mock_ensure, mock_files, mock_process):
        """
        WHAT: Return True on successful rename
        WHY: Pipeline success indicator
        BREAKS: Wrong return value
        """
        mock_files.return_value = ["file.csv"]
        mock_process.return_value = True
        
        result = step_5_rename_columns()
        
        assert result is True
    
    @patch('src.app.pipeline.step_5.handler._get_input_files')
    @patch('src.app.pipeline.step_5.handler.ensure_directory_exists')
    def test_returns_false_when_no_files(self, mock_ensure, mock_files):
        """
        WHAT: Return False when no input files
        WHY: Can't rename without files
        BREAKS: Error on empty directory
        """
        mock_files.return_value = None
        
        result = step_5_rename_columns()
        
        assert result is False

"""Comprehensive tests for Step 3 (Validation) and Step 4 (Analysis) handlers.

Tests cover all functions for data validation and sales analysis.
"""

import os
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import pandas as pd

import pytest

# Step 3 imports
from src.app.pipeline.step_3.handler import (
    _log_date_validation,
    _log_headers_validation,
    _log_overall_result,
    _remove_first_row,
    _perform_validation,
    _handle_post_validation,
    _validate_csv_file,
    _try_validate,
    step_3_validate_data,
)

# Step 4 imports
from src.app.pipeline.step_4.handler import (
    _execute_analysis,
    _process_analysis,
    step_4_sales_analysis,
)


# ===================== Fixtures =====================

@pytest.fixture
def valid_csv_file(tmp_path):
    """Create a valid CSV file with date header."""
    csv_path = tmp_path / "valid.csv"
    csv_path.write_text(
        "01/01/2024 10:00 - 01/04/2024 10:00\n"
        "كود,إسم الصنف,سعر البيع,الشركة,الوحدة,مبيعات الادارة,رصيد الادارة,"
        "مبيعات الشهيد,رصيد الشهيد,مبيعات العشرين,رصيد العشرين,"
        "مبيعات العقبى,رصيد العقبى,مبيعات النجوم,رصيد النجوم,"
        "مبيعات الوردانى,رصيد الوردانى\n"
        "001,Test Product,10.00,Company,Unit,100,50,80,40,60,30,70,35,90,45,85,42\n",
        encoding='utf-8-sig'
    )
    return str(csv_path)


@pytest.fixture
def simple_csv_file(tmp_path):
    """Create a simple CSV file for analysis."""
    csv_path = tmp_path / "simple.csv"
    csv_path.write_text(
        "code,name,value\n"
        "001,Product A,100\n"
        "002,Product B,200\n",
        encoding='utf-8-sig'
    )
    return str(csv_path)


# ===================== Step 3: _log_date_validation Tests =====================

class TestLogDateValidation:
    """Tests for _log_date_validation function."""
    
    def test_logs_valid_date_range(self, caplog):
        """
        WHAT: Log valid date range info
        WHY: User feedback on validation
        BREAKS: Missing validation info
        """
        start = datetime(2024, 1, 1)
        end = datetime(2024, 4, 1)
        
        with caplog.at_level('INFO'):
            _log_date_validation(True, start, end, "Valid date range")
        
        assert "01/01/2024" in caplog.text
        assert ">= 3 months" in caplog.text
    
    def test_logs_invalid_date_range(self, caplog):
        """
        WHAT: Log invalid date range warning
        WHY: User needs to know validation failed
        BREAKS: Silent failure
        """
        start = datetime(2024, 1, 1)
        end = datetime(2024, 2, 1)  # Less than 3 months
        
        with caplog.at_level('INFO'):
            _log_date_validation(False, start, end, "Invalid")
        
        assert "less than 3 months" in caplog.text
    
    def test_handles_none_dates(self, caplog):
        """
        WHAT: Handle None dates gracefully
        WHY: Dates may not be extractable
        BREAKS: NoneType error
        """
        with caplog.at_level('INFO'):
            _log_date_validation(False, None, None, "Could not extract")
        
        assert "Date Range" in caplog.text


# ===================== Step 3: _log_headers_validation Tests =====================

class TestLogHeadersValidation:
    """Tests for _log_headers_validation function."""
    
    def test_logs_valid_headers(self, caplog):
        """
        WHAT: Log successful headers validation
        WHY: Confirm headers are correct
        BREAKS: Missing confirmation
        """
        with caplog.at_level('INFO'):
            _log_headers_validation(True, [], "All columns present")
        
        assert "All column headers" in caplog.text
    
    def test_logs_header_errors(self, caplog):
        """
        WHAT: Log header validation errors
        WHY: User needs to fix errors
        BREAKS: Silent failure on errors
        """
        errors = ["Missing column: code", "Unknown column: extra"]
        
        with caplog.at_level('WARNING'):
            _log_headers_validation(False, errors, "Validation failed")
        
        assert "Missing column" in caplog.text or "failed" in caplog.text


# ===================== Step 3: _remove_first_row Tests =====================

class TestRemoveFirstRow:
    """Tests for _remove_first_row function."""
    
    def test_removes_first_row_successfully(self, tmp_path):
        """
        WHAT: Remove date header row from CSV
        WHY: Data processing needs clean CSV
        BREAKS: Date row interferes with processing
        """
        csv_path = tmp_path / "test.csv"
        csv_path.write_text(
            "Date header line\n"
            "code,name,value\n"
            "001,Test,100\n",
            encoding='utf-8-sig'
        )
        
        result = _remove_first_row(str(csv_path), "test.csv")
        
        assert result is True
        content = csv_path.read_text()
        assert "Date header" not in content
    
    def test_handles_read_error(self):
        """
        WHAT: Return False on read error
        WHY: Graceful error handling
        BREAKS: Unhandled exception
        """
        result = _remove_first_row("/nonexistent/file.csv", "file.csv")
        
        assert result is False


# ===================== Step 3: _log_overall_result Tests =====================

class TestLogOverallResult:
    """Tests for _log_overall_result function."""
    
    def test_logs_success(self, caplog):
        """
        WHAT: Log successful validation result
        WHY: Clear success indication
        BREAKS: Unclear result status
        """
        with caplog.at_level('INFO'):
            _log_overall_result(True)
        
        assert "SUCCESSFUL" in caplog.text
    
    def test_logs_failure(self, caplog):
        """
        WHAT: Log failed validation result
        WHY: Clear failure indication
        BREAKS: Unclear result status
        """
        with caplog.at_level('INFO'):
            _log_overall_result(False)
        
        assert "FAILED" in caplog.text


# ===================== Step 3: step_3_validate_data Tests =====================

class TestStep3ValidateData:
    """Tests for step_3_validate_data main function."""
    
    @patch('src.app.pipeline.step_3.handler._try_validate')
    @patch('src.app.pipeline.step_3.handler.get_csv_files')
    def test_returns_true_on_success(self, mock_files, mock_validate):
        """
        WHAT: Return True on successful validation
        WHY: Pipeline success indicator
        BREAKS: Wrong return value
        """
        mock_files.return_value = ["file.csv"]
        mock_validate.return_value = True
        
        result = step_3_validate_data()
        
        assert result is True
    
    @patch('src.app.pipeline.step_3.handler.get_csv_files')
    def test_returns_false_when_no_files(self, mock_files):
        """
        WHAT: Return False when no CSV files found
        WHY: Can't validate without files
        BREAKS: Error on empty directory
        """
        mock_files.return_value = []
        
        result = step_3_validate_data()
        
        assert result is False


# ===================== Step 3: _try_validate Tests =====================

class TestTryValidate:
    """Tests for _try_validate function."""
    
    @patch('src.app.pipeline.step_3.handler._validate_csv_file')
    def test_handles_value_error(self, mock_validate, tmp_path):
        """
        WHAT: Handle ValueError gracefully
        WHY: User input errors shouldn't crash
        BREAKS: Unhandled user input error
        """
        mock_validate.side_effect = ValueError("Invalid input")
        
        result = _try_validate(str(tmp_path), ["file.csv"], True)
        
        assert result is False
    
    @patch('src.app.pipeline.step_3.handler._validate_csv_file')
    def test_handles_general_exception(self, mock_validate, tmp_path):
        """
        WHAT: Handle general exceptions
        WHY: Graceful error handling
        BREAKS: Unhandled exception
        """
        mock_validate.side_effect = Exception("Unexpected error")
        
        result = _try_validate(str(tmp_path), ["file.csv"], True)
        
        assert result is False


# ===================== Step 4: _execute_analysis Tests =====================

class TestExecuteAnalysis:
    """Tests for _execute_analysis function."""
    
    @patch('src.app.pipeline.step_4.handler.generate_report')
    @patch('src.app.pipeline.step_4.handler.analyze_csv_data')
    def test_returns_true_on_success(self, mock_analyze, mock_report, simple_csv_file):
        """
        WHAT: Return True after successful analysis
        WHY: Confirm analysis completed
        BREAKS: False return on success
        """
        mock_analyze.return_value = {'total_rows': 10}
        mock_report.return_value = "Report content"
        
        result = _execute_analysis(simple_csv_file, "simple.csv")
        
        assert result is True
        mock_analyze.assert_called_once()
        mock_report.assert_called_once()


# ===================== Step 4: _process_analysis Tests =====================

class TestProcessAnalysis:
    """Tests for _process_analysis function."""
    
    @patch('src.app.pipeline.step_4.handler._execute_analysis')
    @patch('src.app.pipeline.step_4.handler.select_csv_file')
    @patch('src.app.pipeline.step_4.handler.get_file_path')
    def test_calls_execute_analysis(self, mock_path, mock_select, mock_execute, tmp_path):
        """
        WHAT: Call _execute_analysis with correct params
        WHY: Analysis should be performed
        BREAKS: Analysis never runs
        """
        mock_select.return_value = "file.csv"
        mock_path.return_value = str(tmp_path / "file.csv")
        mock_execute.return_value = True
        
        result = _process_analysis(str(tmp_path), ["file.csv"], True)
        
        mock_execute.assert_called_once()
    
    @patch('src.app.pipeline.step_4.handler.select_csv_file')
    def test_handles_value_error(self, mock_select, tmp_path):
        """
        WHAT: Handle ValueError from select
        WHY: Invalid selection shouldn't crash
        BREAKS: Unhandled error
        """
        mock_select.side_effect = ValueError("Invalid selection")
        
        result = _process_analysis(str(tmp_path), ["file.csv"], True)
        
        assert result is False
    
    @patch('src.app.pipeline.step_4.handler.select_csv_file')
    def test_handles_general_exception(self, mock_select, tmp_path):
        """
        WHAT: Handle general exceptions
        WHY: Graceful error handling
        BREAKS: Unhandled exception
        """
        mock_select.side_effect = Exception("Error")
        
        result = _process_analysis(str(tmp_path), ["file.csv"], True)
        
        assert result is False


# ===================== Step 4: step_4_sales_analysis Tests =====================

class TestStep4SalesAnalysis:
    """Tests for step_4_sales_analysis main function."""
    
    @patch('src.app.pipeline.step_4.handler._process_analysis')
    @patch('src.app.pipeline.step_4.handler.get_csv_files')
    def test_returns_true_on_success(self, mock_files, mock_process):
        """
        WHAT: Return True on successful analysis
        WHY: Pipeline success indicator
        BREAKS: Wrong return value
        """
        mock_files.return_value = ["file.csv"]
        mock_process.return_value = True
        
        result = step_4_sales_analysis()
        
        assert result is True
    
    @patch('src.app.pipeline.step_4.handler.get_csv_files')
    def test_returns_false_when_no_files(self, mock_files):
        """
        WHAT: Return False when no CSV files
        WHY: Can't analyze without files
        BREAKS: Error on empty directory
        """
        mock_files.return_value = []
        
        result = step_4_sales_analysis()
        
        assert result is False

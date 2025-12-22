"""Comprehensive tests for Step 7 transfer generation handler."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.app.pipeline.step_7.handler import (
    _validate_analytics_directories,
    _get_analytics_files,
    _extract_date_header_info,
    _group_files_by_source,
    _log_source_files,
    _log_transfer_summary,
    _validate_and_get_files,
    _execute_transfer_generation,
    _run_transfer_generation,
    step_7_generate_transfers,
    _format_file_size,
)


# ===================== Fixtures =====================

@pytest.fixture
def analytics_directory(tmp_path):
    """Create a mock analytics directory with branch subdirs."""
    analytics_dir = tmp_path / "analytics"
    
    for branch in ["admin", "wardani", "akba"]:
        branch_dir = analytics_dir / branch
        branch_dir.mkdir(parents=True)
        (branch_dir / f"{branch}_analytics.csv").write_text("code,name,balance\n001,Product,100")
    
    return str(analytics_dir)


@pytest.fixture
def empty_analytics_directory(tmp_path):
    """Create analytics directory with empty branch dirs."""
    analytics_dir = tmp_path / "empty_analytics"
    
    for branch in ["admin", "wardani"]:
        (analytics_dir / branch).mkdir(parents=True)
    
    return str(analytics_dir)


# ===================== _validate_analytics_directories Tests =====================

class TestValidateAnalyticsDirectories:
    """Tests for _validate_analytics_directories function."""
    
    def test_returns_true_when_all_exist(self, analytics_directory):
        """
        WHAT: Return True when all branch directories exist
        WHY: Validation should pass with valid structure
        BREAKS: False negative on valid directories
        """
        result = _validate_analytics_directories(analytics_directory, ["admin", "wardani"])
        
        assert result is True
    
    def test_returns_false_when_branch_missing(self, analytics_directory):
        """
        WHAT: Return False when branch directory missing
        WHY: Must fail before processing invalid data
        BREAKS: Crash on missing directory
        """
        result = _validate_analytics_directories(analytics_directory, ["admin", "nonexistent"])
        
        assert result is False
    
    def test_returns_false_for_nonexistent_base(self):
        """
        WHAT: Return False for nonexistent base directory
        WHY: Early validation prevents later errors
        BREAKS: FileNotFoundError during processing
        """
        result = _validate_analytics_directories("/nonexistent/path", ["admin"])
        
        assert result is False


# ===================== _get_analytics_files Tests =====================

class TestGetAnalyticsFiles:
    """Tests for _get_analytics_files function."""
    
    def test_returns_files_for_branches(self, analytics_directory):
        """
        WHAT: Return dict of CSV files per branch
        WHY: Need to locate files for processing
        BREAKS: Can't find analytics files
        """
        result = _get_analytics_files(analytics_directory, ["admin", "wardani"])
        
        assert "admin" in result
        assert len(result["admin"]) >= 1
    
    def test_skips_branches_without_files(self, empty_analytics_directory):
        """
        WHAT: Don't include branches without CSV files
        WHY: Avoid empty entries in result
        BREAKS: KeyError on empty branches
        """
        result = _get_analytics_files(empty_analytics_directory, ["admin", "wardani"])
        
        # Should be empty since no CSV files exist
        assert len(result) == 0


# ===================== _group_files_by_source Tests =====================

class TestGroupFilesBySource:
    """Tests for _group_files_by_source function."""
    
    def test_groups_by_source_branch(self):
        """
        WHAT: Group transfer files by source branch
        WHY: Organized logging and processing
        BREAKS: Scattered file listing
        """
        transfer_files = {
            ("admin", "wardani"): "/path/to/admin_to_wardani.csv",
            ("admin", "akba"): "/path/to/admin_to_akba.csv",
            ("wardani", "admin"): "/path/to/wardani_to_admin.csv",
        }
        
        result = _group_files_by_source(transfer_files)
        
        assert "admin" in result
        assert len(result["admin"]) == 2
        assert "wardani" in result
        assert len(result["wardani"]) == 1
    
    def test_handles_empty_dict(self):
        """
        WHAT: Handle empty transfer files dict
        WHY: Edge case when no transfers generated
        BREAKS: Exception on empty input
        """
        result = _group_files_by_source({})
        
        assert result == {}


# ===================== _format_file_size Tests =====================

class TestFormatFileSize:
    """Tests for _format_file_size function."""
    
    def test_formats_zero_bytes(self):
        """
        WHAT: Format zero bytes correctly
        WHY: Edge case for empty files
        BREAKS: Division by zero
        """
        result = _format_file_size(0)
        
        assert result == "0 B"
    
    def test_formats_bytes(self):
        """
        WHAT: Format small sizes as bytes
        WHY: Human-readable output
        BREAKS: Wrong unit displayed
        """
        result = _format_file_size(512)
        
        assert "B" in result
        assert "512" in result
    
    def test_formats_kilobytes(self):
        """
        WHAT: Format KB-range sizes
        WHY: Appropriate unit selection
        BREAKS: Shows bytes for large files
        """
        result = _format_file_size(2048)
        
        assert "KB" in result
    
    def test_formats_megabytes(self):
        """
        WHAT: Format MB-range sizes
        WHY: Typical file sizes
        BREAKS: Wrong unit for MB files
        """
        result = _format_file_size(5 * 1024 * 1024)
        
        assert "MB" in result
    
    def test_formats_gigabytes(self):
        """
        WHAT: Format GB-range sizes
        WHY: Large output support
        BREAKS: Overflow on large files
        """
        result = _format_file_size(2 * 1024 * 1024 * 1024)
        
        assert "GB" in result


# ===================== _validate_and_get_files Tests =====================

class TestValidateAndGetFiles:
    """Tests for _validate_and_get_files function."""
    
    def test_returns_files_when_valid(self, analytics_directory):
        """
        WHAT: Return analytics files for valid directory
        WHY: Combined validation and retrieval
        BREAKS: None returned for valid input
        """
        result = _validate_and_get_files(analytics_directory, ["admin", "wardani"])
        
        assert result is not None
        assert len(result) >= 1
    
    def test_returns_none_when_invalid(self):
        """
        WHAT: Return None for invalid directory
        WHY: Caller can check for failure
        BREAKS: Exception instead of None
        """
        result = _validate_and_get_files("/nonexistent", ["admin"])
        
        assert result is None


# ===================== _run_transfer_generation Tests =====================

class TestRunTransferGeneration:
    """Tests for _run_transfer_generation function."""
    
    @patch('src.app.pipeline.step_7.handler._execute_transfer_generation')
    def test_returns_success_on_completion(self, mock_execute, analytics_directory):
        """
        WHAT: Return True when generation succeeds
        WHY: Caller needs success indicator
        BREAKS: Wrong return value
        """
        mock_execute.return_value = True
        
        result = _run_transfer_generation(analytics_directory, "/output", {"admin": ["file.csv"]})
        
        assert result is True
    
    @patch('src.app.pipeline.step_7.handler._execute_transfer_generation')
    def test_handles_value_error(self, mock_execute, analytics_directory):
        """
        WHAT: Handle ValueError gracefully
        WHY: Some validation errors are expected
        BREAKS: Crash on validation error
        """
        mock_execute.side_effect = ValueError("Test error")
        
        result = _run_transfer_generation(analytics_directory, "/output", {"admin": ["file.csv"]})
        
        assert result is False
    
    @patch('src.app.pipeline.step_7.handler._execute_transfer_generation')
    def test_handles_general_exception(self, mock_execute, analytics_directory):
        """
        WHAT: Handle general exceptions gracefully
        WHY: Unexpected errors shouldn't crash
        BREAKS: Unhandled exception
        """
        mock_execute.side_effect = Exception("Unexpected error")
        
        result = _run_transfer_generation(analytics_directory, "/output", {"admin": ["file.csv"]})
        
        assert result is False


# ===================== step_7_generate_transfers Tests =====================

class TestStep7GenerateTransfers:
    """Tests for step_7_generate_transfers main function."""
    
    @patch('src.app.pipeline.step_7.handler._run_transfer_generation')
    @patch('src.app.pipeline.step_7.handler._validate_and_get_files')
    @patch('src.app.pipeline.step_7.handler.get_branches')
    def test_calls_generation_on_valid_input(self, mock_branches, mock_validate, mock_run):
        """
        WHAT: Call generation when input is valid
        WHY: Main workflow should proceed
        BREAKS: Generation never called
        """
        mock_branches.return_value = ["admin", "wardani"]
        mock_validate.return_value = {"admin": ["file.csv"]}
        mock_run.return_value = True
        
        result = step_7_generate_transfers()
        
        mock_run.assert_called_once()
        assert result is True
    
    @patch('src.app.pipeline.step_7.handler._validate_and_get_files')
    @patch('src.app.pipeline.step_7.handler.get_branches')
    def test_returns_false_on_invalid_input(self, mock_branches, mock_validate):
        """
        WHAT: Return False when validation fails
        WHY: Don't proceed with invalid data
        BREAKS: Crash on invalid input
        """
        mock_branches.return_value = ["admin"]
        mock_validate.return_value = None
        
        result = step_7_generate_transfers()
        
        assert result is False


# ===================== _extract_date_header_info Tests =====================

class TestExtractDateHeaderInfo:
    """Tests for _extract_date_header_info function."""
    
    def test_returns_tuple_on_success(self, analytics_directory):
        """
        WHAT: Return (has_date_header, first_line) tuple
        WHY: Caller needs both values
        BREAKS: Wrong return type
        """
        analytics_files = {"admin": ["admin_analytics.csv"]}
        
        result = _extract_date_header_info(analytics_directory, analytics_files)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_handles_exception_gracefully(self):
        """
        WHAT: Return (False, "") on exception
        WHY: Graceful error handling
        BREAKS: Crash on malformed file
        """
        result = _extract_date_header_info("/nonexistent", {"admin": ["file.csv"]})
        
        assert result == (False, "")

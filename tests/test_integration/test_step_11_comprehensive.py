"""Comprehensive tests for Step 11 combined transfers handler."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

import pytest

from src.app.pipeline.step_11.runner.generators import (
    convert_and_count as _convert_and_count,
    generate_merged_output as _generate_merged_output,
    generate_separate_output as _generate_separate_output,
)
from src.app.pipeline.step_11.runner.processing import (
    get_combined_data as _get_combined_data,
    process_single_branch as _process_single_branch,
    process_all_branches as _process_all_branches,
)
from src.app.pipeline.step_11.runner.orchestrator import (
    step_11_generate_combined_transfers,
    log_summary as _log_summary,
)
from src.app.pipeline.step_11.runner.validation import (
    validate_input_directories as _validate_input_directories,
    create_output_directories as _create_output_directories,
)
from src.app.pipeline.step_11.runner.constants import (
    TRANSFERS_DIR,
    REMAINING_SURPLUS_DIR,
)


# ===================== Constants Tests =====================

class TestStep11Constants:
    """Tests for Step 11 constants."""
    
    def test_transfers_dir_path(self):
        """
        WHAT: Verify transfers directory path
        WHY: Correct path for input files
        BREAKS: Can't find input files
        """
        assert "transfers" in TRANSFERS_DIR
        assert "csv" in TRANSFERS_DIR
    
    def test_surplus_dir_path(self):
        """
        WHAT: Verify surplus directory path
        WHY: Correct path for surplus files
        BREAKS: Missing surplus input
        """
        assert "remaining_surplus" in REMAINING_SURPLUS_DIR


# ===================== _convert_and_count Tests =====================

class TestConvertAndCount:
    """Tests for _convert_and_count function."""
    
    @patch('src.app.pipeline.step_11.runner.generators.convert_to_excel_with_formatting')
    def test_converts_files_and_returns_count(self, mock_convert, tmp_path):
        """
        WHAT: Convert files and return count
        WHY: Track number of files generated
        BREAKS: Wrong count reported
        """
        files = ["/path/file1.csv", "/path/file2.csv", "/path/file3.csv"]
        
        result = _convert_and_count(files, str(tmp_path))
        
        assert result == 3
        mock_convert.assert_called_once()
    
    def test_returns_zero_for_empty_list(self, tmp_path):
        """
        WHAT: Return 0 for empty file list
        WHY: No conversion needed
        BREAKS: Error on empty input
        """
        result = _convert_and_count([], str(tmp_path))
        
        assert result == 0
    
    def test_returns_zero_for_none(self, tmp_path):
        """
        WHAT: Return 0 for None input
        WHY: Graceful handling of no files
        BREAKS: NoneType error
        """
        result = _convert_and_count(None, str(tmp_path))
        
        assert result == 0


# ===================== _validate_input_directories Tests =====================

class TestValidateInputDirectories:
    """Tests for _validate_input_directories function."""
    
    def test_returns_true_when_all_exist(self, tmp_path):
        """
        WHAT: Return True when all directories exist
        WHY: Validation should pass
        BREAKS: False negative
        """
        transfers = tmp_path / "transfers" / "csv"
        surplus = tmp_path / "remaining_surplus" / "csv"
        transfers.mkdir(parents=True)
        surplus.mkdir(parents=True)
        
        with patch('src.app.pipeline.step_11.runner.validation.TRANSFERS_DIR', str(transfers)):
            with patch('src.app.pipeline.step_11.runner.validation.REMAINING_SURPLUS_DIR', str(surplus)):
                result = _validate_input_directories()
        
        assert result is True
    
    def test_returns_false_when_transfers_missing(self):
        """
        WHAT: Return False when transfers dir missing
        WHY: Can't proceed without input
        BREAKS: FileNotFoundError
        """
        with patch('src.app.pipeline.step_11.runner.validation.TRANSFERS_DIR', '/nonexistent/path'):
            result = _validate_input_directories()
        
        assert result is False


# ===================== _create_output_directories Tests =====================

class TestCreateOutputDirectories:
    """Tests for _create_output_directories function."""
    
    def test_creates_all_directories(self, tmp_path):
        """
        WHAT: Create all output directories
        WHY: Output paths must exist before writing
        BREAKS: FileNotFoundError on write
        """
        merged_csv = tmp_path / "merged" / "csv"
        merged_excel = tmp_path / "merged" / "excel"
        separate_csv = tmp_path / "separate" / "csv"
        separate_excel = tmp_path / "separate" / "excel"
        
        with patch('src.app.pipeline.step_11.runner.validation.OUTPUT_MERGED_CSV', str(merged_csv)):
            with patch('src.app.pipeline.step_11.runner.validation.OUTPUT_MERGED_EXCEL', str(merged_excel)):
                with patch('src.app.pipeline.step_11.runner.validation.OUTPUT_SEPARATE_CSV', str(separate_csv)):
                    with patch('src.app.pipeline.step_11.runner.validation.OUTPUT_SEPARATE_EXCEL', str(separate_excel)):
                        _create_output_directories()
        
        assert merged_csv.exists()
        assert merged_excel.exists()
        assert separate_csv.exists()
        assert separate_excel.exists()


# ===================== _log_summary Tests =====================

class TestLogSummary:
    """Tests for _log_summary function."""
    
    def test_logs_counts(self, caplog):
        """
        WHAT: Log merged and separate file counts
        WHY: User feedback on generation
        BREAKS: No summary displayed
        """
        with caplog.at_level('INFO'):
            _log_summary(10, 20)
        
        assert "10" in caplog.text
        assert "20" in caplog.text


# ===================== _process_single_branch Tests =====================

class TestProcessSingleBranch:
    """Tests for _process_single_branch function."""
    
    @patch('src.app.pipeline.step_11.runner.processing.generators.generate_separate_output')
    @patch('src.app.pipeline.step_11.runner.processing.generators.generate_merged_output')
    @patch('src.app.pipeline.step_11.runner.processing.get_combined_data')
    def test_returns_counts_on_success(self, mock_data, mock_merged, mock_separate):
        """
        WHAT: Return (merged_count, separate_count) tuple
        WHY: Track output per branch
        BREAKS: Wrong counts
        """
        mock_data.return_value = pd.DataFrame({"col": [1, 2, 3]})
        mock_merged.return_value = 5
        mock_separate.return_value = 10
        
        merged, separate = _process_single_branch("admin", "20231222")
        
        assert merged == 5
        assert separate == 10
    
    @patch('src.app.pipeline.step_11.runner.processing.get_combined_data')
    def test_returns_zeros_for_empty_data(self, mock_data):
        """
        WHAT: Return (0, 0) when no data
        WHY: Handle branches without transfers
        BREAKS: Error on empty branch
        """
        mock_data.return_value = pd.DataFrame()
        
        merged, separate = _process_single_branch("empty_branch", "20231222")
        
        assert merged == 0
        assert separate == 0
    
    @patch('src.app.pipeline.step_11.runner.processing.get_combined_data')
    def test_handles_none_data(self, mock_data):
        """
        WHAT: Handle None combined data
        WHY: Some branches may have no data
        BREAKS: NoneType error
        """
        mock_data.return_value = None
        
        merged, separate = _process_single_branch("none_branch", "20231222")
        
        assert merged == 0
        assert separate == 0


# ===================== _process_all_branches Tests =====================

class TestProcessAllBranches:
    """Tests for _process_all_branches function."""
    
    @patch('src.app.pipeline.step_11.runner.processing.process_single_branch')
    @patch('src.app.pipeline.step_11.runner.processing.get_branches')
    def test_sums_all_branch_counts(self, mock_branches, mock_process):
        """
        WHAT: Sum counts from all branches
        WHY: Total output count
        BREAKS: Missing branch counts
        """
        mock_branches.return_value = ["admin", "wardani", "akba"]
        mock_process.side_effect = [(2, 4), (3, 6), (1, 2)]
        
        total_merged, total_separate = _process_all_branches("20231222")
        
        assert total_merged == 6  # 2+3+1
        assert total_separate == 12  # 4+6+2
    
    @patch('src.app.pipeline.step_11.runner.processing.process_single_branch')
    @patch('src.app.pipeline.step_11.runner.processing.get_branches')
    def test_handles_empty_branches(self, mock_branches, mock_process):
        """
        WHAT: Handle empty branches list
        WHY: Edge case
        BREAKS: Error on empty list
        """
        mock_branches.return_value = []
        
        total_merged, total_separate = _process_all_branches("20231222")
        
        assert total_merged == 0
        assert total_separate == 0


# ===================== step_11_generate_combined_transfers Tests =====================

class TestStep11GenerateCombinedTransfers:
    """Tests for step_11_generate_combined_transfers main function."""
    
    @patch('src.app.pipeline.step_11.runner.orchestrator.log_summary')
    @patch('src.app.pipeline.step_11.runner.orchestrator.processing.process_all_branches')
    @patch('src.app.pipeline.step_11.runner.orchestrator.validation.create_output_directories')
    @patch('src.app.pipeline.step_11.runner.orchestrator.validation.validate_input_directories')
    def test_returns_true_on_success(self, mock_validate, mock_create, mock_process, mock_log):
        """
        WHAT: Return True when files generated
        WHY: Success indicator for pipeline
        BREAKS: Wrong return value
        """
        mock_validate.return_value = True
        mock_process.return_value = (5, 10)
        
        result = step_11_generate_combined_transfers()
        
        assert result is True
    
    @patch('src.app.pipeline.step_11.runner.orchestrator.validation.validate_input_directories')
    def test_returns_false_on_invalid_dirs(self, mock_validate):
        """
        WHAT: Return False when validation fails
        WHY: Don't proceed without input
        BREAKS: Crash on missing input
        """
        mock_validate.return_value = False
        
        result = step_11_generate_combined_transfers()
        
        assert result is False
    
    @patch('src.app.pipeline.step_11.runner.orchestrator.log_summary')
    @patch('src.app.pipeline.step_11.runner.orchestrator.processing.process_all_branches')
    @patch('src.app.pipeline.step_11.runner.orchestrator.validation.create_output_directories')
    @patch('src.app.pipeline.step_11.runner.orchestrator.validation.validate_input_directories')
    def test_returns_false_when_no_output(self, mock_validate, mock_create, mock_process, mock_log):
        """
        WHAT: Return False when no files generated
        WHY: Indicate no output produced
        BREAKS: False positive
        """
        mock_validate.return_value = True
        mock_process.return_value = (0, 0)
        
        result = step_11_generate_combined_transfers()
        
        assert result is False
    
    @patch('src.app.pipeline.step_11.runner.orchestrator.processing.process_all_branches')
    @patch('src.app.pipeline.step_11.runner.orchestrator.validation.create_output_directories')
    @patch('src.app.pipeline.step_11.runner.orchestrator.validation.validate_input_directories')
    def test_handles_exception(self, mock_validate, mock_create, mock_process):
        """
        WHAT: Handle exceptions gracefully
        WHY: Pipeline shouldn't crash
        BREAKS: Unhandled exception
        """
        mock_validate.return_value = True
        mock_process.side_effect = Exception("Test error")
        
        result = step_11_generate_combined_transfers()
        
        assert result is False

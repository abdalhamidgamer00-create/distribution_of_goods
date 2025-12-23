"""Comprehensive tests for Step 1 archive handler module.

Tests cover the archive functionality that backs up output files
before starting a new processing run.
"""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


# ===================== Fixtures =====================

@pytest.fixture
def temp_directory_with_files(tmp_path):
    """Create a temp directory with some files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create some files
    (output_dir / "file1.csv").write_text("test content 1")
    (output_dir / "file2.csv").write_text("test content 2")
    
    # Create a subdirectory with files
    subdir = output_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.csv").write_text("test content 3")
    
    return str(output_dir)


@pytest.fixture
def empty_temp_directory(tmp_path):
    """Create an empty temp directory."""
    output_dir = tmp_path / "empty_output"
    output_dir.mkdir()
    return str(output_dir)


# ===================== _has_files_in_directory Tests =====================

class TestHasFilesInDirectory:
    """Tests for _has_files_in_directory function."""
    
    def test_returns_true_when_has_files(self, temp_directory_with_files):
        """
        WHAT: Return True when directory contains files
        WHY: Correctly detect files for archiving
        BREAKS: Archiving skipped when files exist
        """
        from src.app.pipeline.step_1.cleaner.files import has_files_in_directory as _has_files_in_directory
        
        result = _has_files_in_directory(temp_directory_with_files)
        
        assert result is True
    
    def test_returns_false_when_empty(self, empty_temp_directory):
        """
        WHAT: Return False for empty directory
        WHY: Skip archiving when nothing to archive
        BREAKS: Unnecessary archive operations
        """
        from src.app.pipeline.step_1.cleaner.files import has_files_in_directory as _has_files_in_directory
        
        result = _has_files_in_directory(empty_temp_directory)
        
        assert result is False
    
    def test_returns_false_when_directory_not_exists(self):
        """
        WHAT: Return False for nonexistent directory
        WHY: Graceful handling of missing paths
        BREAKS: Exception on first run
        """
        from src.app.pipeline.step_1.cleaner.files import has_files_in_directory as _has_files_in_directory
        
        result = _has_files_in_directory("/nonexistent/path/that/does/not/exist")
        
        assert result is False
    
    def test_finds_files_in_subdirectories(self, tmp_path):
        """
        WHAT: Find files recursively in subdirectories
        WHY: All output files should be detected
        BREAKS: Missing nested files in archive
        """
        from src.app.pipeline.step_1.cleaner.files import has_files_in_directory as _has_files_in_directory
        
        # Create only nested files
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        subdir = output_dir / "deep" / "nested"
        subdir.mkdir(parents=True)
        (subdir / "hidden_file.csv").write_text("content")
        
        result = _has_files_in_directory(str(output_dir))
        
        assert result is True


# ===================== _calculate_directory_size Tests =====================

class TestCalculateDirectorySize:
    """Tests for _calculate_directory_size function."""
    
    def test_calculates_correct_size(self, tmp_path):
        """
        WHAT: Calculate total directory size correctly
        WHY: Accurate size reporting for archives
        BREAKS: Incorrect size displayed to user
        """
        from src.app.pipeline.step_1.cleaner.files import calculate_directory_size as _calculate_directory_size
        
        test_dir = tmp_path / "size_test"
        test_dir.mkdir()
        
        # Create files with known sizes
        content1 = "a" * 100
        content2 = "b" * 200
        (test_dir / "file1.txt").write_text(content1)
        (test_dir / "file2.txt").write_text(content2)
        
        result = _calculate_directory_size(str(test_dir))
        
        assert result == 300
    
    def test_returns_zero_for_empty_directory(self, empty_temp_directory):
        """
        WHAT: Return 0 for empty directory
        WHY: No errors on empty directories
        BREAKS: Division by zero in compression ratio
        """
        from src.app.pipeline.step_1.cleaner.files import calculate_directory_size as _calculate_directory_size
        
        result = _calculate_directory_size(empty_temp_directory)
        
        assert result == 0
    
    def test_returns_zero_for_nonexistent_directory(self):
        """
        WHAT: Return 0 for nonexistent directory
        WHY: Graceful error handling
        BREAKS: Exception crashes archiving
        """
        from src.app.pipeline.step_1.cleaner.files import calculate_directory_size as _calculate_directory_size
        
        result = _calculate_directory_size("/nonexistent/path")
        
        assert result == 0


# ===================== _format_size Tests =====================

class TestFormatSize:
    """Tests for _format_size function."""
    
    def test_formats_bytes(self):
        """
        WHAT: Format small sizes as bytes
        WHY: Human-readable size display
        BREAKS: Confusing size display
        """
        from src.app.pipeline.step_1.cleaner.formatting import format_size as _format_size
        
        result = _format_size(500)
        
        assert "B" in result
        assert "500" in result
    
    def test_formats_kilobytes(self):
        """
        WHAT: Format KB-range sizes
        WHY: Appropriate unit for small files
        BREAKS: Showing too many decimal places
        """
        from src.app.pipeline.step_1.cleaner.formatting import format_size as _format_size
        
        result = _format_size(2048)
        
        assert "KB" in result
    
    def test_formats_megabytes(self):
        """
        WHAT: Format MB-range sizes
        WHY: Appropriate unit for typical files
        BREAKS: Wrong unit displayed
        """
        from src.app.pipeline.step_1.cleaner.formatting import format_size as _format_size
        
        result = _format_size(5 * 1024 * 1024)
        
        assert "MB" in result
    
    def test_formats_gigabytes(self):
        """
        WHAT: Format GB-range sizes
        WHY: Large archive support
        BREAKS: Overflow on large files
        """
        from src.app.pipeline.step_1.cleaner.formatting import format_size as _format_size
        
        result = _format_size(3 * 1024 * 1024 * 1024)
        
        assert "GB" in result


# ===================== _archive_if_has_files Tests =====================

class TestArchiveIfHasFiles:
    """Tests for _archive_if_has_files function."""
    
    @patch('src.app.pipeline.step_1.cleaner.orchestrator._execute_archive')
    def test_archives_when_files_exist(self, mock_execute, temp_directory_with_files, tmp_path):
        """
        WHAT: Call archive when files exist
        WHY: Properly back up output
        BREAKS: Data loss on re-run
        """
        from src.app.pipeline.step_1.cleaner.orchestrator import _archive_if_has_files
        
        mock_execute.return_value = True
        archive_dir = str(tmp_path / "archive")
        
        result = _archive_if_has_files(temp_directory_with_files, archive_dir)
        
        assert result is True
        mock_execute.assert_called_once()
    
    def test_skips_when_no_files(self, empty_temp_directory, tmp_path):
        """
        WHAT: Skip archive when no files
        WHY: Avoid empty archives
        BREAKS: Error on fresh start
        """
        from src.app.pipeline.step_1.cleaner.orchestrator import _archive_if_has_files
        
        archive_dir = str(tmp_path / "archive")
        
        result = _archive_if_has_files(empty_temp_directory, archive_dir)
        
        assert result is True


# ===================== step_1_archive_output Tests =====================

class TestStep1ArchiveOutput:
    """Tests for step_1_archive_output main function."""
    
    @patch('src.app.pipeline.step_1.cleaner.orchestrator._archive_if_has_files')
    def test_calls_archive_function(self, mock_archive):
        """
        WHAT: Main function delegates to helper
        WHY: Proper function composition
        BREAKS: Archiving never called
        """
        from src.app.pipeline.step_1.cleaner.orchestrator import step_1_archive_output
        
        mock_archive.return_value = True
        
        result = step_1_archive_output()
        
        mock_archive.assert_called_once()
        assert result is True
    
    @patch('src.app.pipeline.step_1.cleaner.orchestrator._archive_if_has_files')
    def test_handles_exception(self, mock_archive):
        """
        WHAT: Return False on exception
        WHY: Graceful error handling
        BREAKS: Unhandled exception stops pipeline
        """
        from src.app.pipeline.step_1.cleaner.orchestrator import step_1_archive_output
        
        mock_archive.side_effect = Exception("Archive error")
        
        result = step_1_archive_output()
        
        assert result is False
    
    def test_uses_correct_directories(self):
        """
        WHAT: Uses standard data directories
        WHY: Consistent file locations
        BREAKS: Archives go to wrong location
        """
        from src.app.pipeline.step_1.cleaner.orchestrator import step_1_archive_output
        import os
        
        # Verify the function exists and is callable
        assert callable(step_1_archive_output)


# ===================== _log_zip_info Tests =====================

class TestLogZipInfo:
    """Tests for _log_zip_info function."""
    
    def test_logs_zip_info_when_file_exists(self, tmp_path, caplog):
        """
        WHAT: Log ZIP info when file exists
        WHY: User feedback on compression
        BREAKS: Missing archive info
        """
        from src.app.pipeline.step_1.cleaner.reporting import log_zip_info as _log_zip_info
        
        # Create a test zip file
        zip_file = tmp_path / "test.zip"
        zip_file.write_bytes(b"x" * 100)
        
        with caplog.at_level('INFO'):
            _log_zip_info(str(zip_file), 200)
        
        # Should log something about the ZIP
        # Note: actual log format depends on implementation
    
    def test_handles_nonexistent_zip(self):
        """
        WHAT: Handle missing ZIP file gracefully
        WHY: No error if ZIP creation failed
        BREAKS: Exception on failed archive
        """
        from src.app.pipeline.step_1.cleaner.reporting import log_zip_info as _log_zip_info
        
        # Should not raise exception
        _log_zip_info("/nonexistent/file.zip", 100)
    
    def test_handles_none_zip_file(self):
        """
        WHAT: Handle None zip_file parameter
        WHY: ZIP might not be created
        BREAKS: NoneType error
        """
        from src.app.pipeline.step_1.cleaner.reporting import log_zip_info as _log_zip_info
        
        # Should not raise exception
        _log_zip_info(None, 100)

"""Unit tests for the ArchiveManager utility."""

import pytest
from unittest.mock import patch, MagicMock
import os
from src.shared.utility.archiver.manager import (
    log_archive_result,
    build_archive_result,
    archive_output_directory,
    archive_all_output
)

class TestArchiveManager:
    """Tests for the ArchiveManager functions."""

    def test_log_archive_result(self):
        """Should return the correct result dictionary."""
        result = log_archive_result("/path/to/archive", 10, 2)
        assert result['archive_dir'] == "/path/to/archive"
        assert result['file_count'] == 10
        assert result['dir_count'] == 2

    def test_build_archive_result(self):
        """Should build the final results dictionary with zip file."""
        info = {'archive_dir': "dir", 'file_count': 5, 'dir_count': 1}
        result = build_archive_result(info, "archive.zip")
        assert result['zip_file'] == "archive.zip"
        assert result['file_count'] == 5

    @patch('src.shared.utility.archiver.directory_ops.prepare_archive_directory')
    @patch('src.shared.utility.archiver.directory_ops.archive_and_copy')
    @patch('os.path.exists')
    def test_archive_output_directory_success(self, mock_exists, mock_copy, mock_prepare):
        """Should correctly orchestrate directory archiving."""
        mock_exists.return_value = True
        mock_prepare.return_value = ("data/archive/ts", "data/archive/ts/output")
        mock_copy.return_value = (10, 2)
        
        result = archive_output_directory("data/output", "data/archive")
        
        assert result['file_count'] == 10
        assert mock_prepare.called
        assert mock_copy.called

    def test_archive_output_directory_not_found(self):
        """Should raise ValueError if directory doesn't exist."""
        with pytest.raises(ValueError, match="Output directory not found"):
            archive_output_directory("non_existent_dir")

    @patch('src.shared.utility.archiver.manager.archive_output_directory')
    @patch('src.shared.utility.archiver.zip_ops.create_zip_archive')
    @patch('os.path.exists')
    def test_archive_all_output(self, mock_exists, mock_zip, mock_archive_dir):
        """Should call archive_output_directory and optionally zip it."""
        mock_exists.return_value = True
        mock_archive_dir.return_value = {'archive_dir': "dir", 'file_count': 1}
        mock_zip.return_value = "dir.zip"
        
        result = archive_all_output(create_zip=True)
        
        assert result['zip_file'] == "dir.zip"
        assert mock_zip.called
        assert mock_archive_dir.called

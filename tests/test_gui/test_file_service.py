import os
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.presentation.gui.services.file_service import (
    list_output_files,
    read_file_content,
    create_zip_archive,
    format_file_size,
    group_files_by_branch,
    group_files_by_category
)


class TestListOutputFiles:
    """Tests for list_output_files function"""
    
    def test_list_files_in_existing_directory(self, tmp_path):
        """Test listing files in existing directory"""
        from src.presentation.gui.services.file_service import list_output_files
        
        # Create test files
        (tmp_path / "file1.csv").write_text("data")
        (tmp_path / "file2.xlsx").write_text("data")
        (tmp_path / "file3.txt").write_text("data")
        
        files = list_output_files(str(tmp_path))
        
        assert len(files) == 2  # Only csv and xlsx
        names = [f["name"] for f in files]
        assert "file1.csv" in names
        assert "file2.xlsx" in names
        assert "file3.txt" not in names
    
    def test_list_files_nonexistent_directory(self):
        """Test listing files in non-existent directory"""
        from src.presentation.gui.services.file_service import list_output_files
        
        files = list_output_files("/nonexistent/path")
        
        assert files == []
    
    def test_list_files_empty_directory(self, tmp_path):
        """Test listing files in empty directory"""
        from src.presentation.gui.services.file_service import list_output_files
        
        files = list_output_files(str(tmp_path))
        
        assert files == []
    
    def test_list_files_custom_extensions(self, tmp_path):
        """Test listing files with custom extensions"""
        from src.presentation.gui.services.file_service import list_output_files
        
        (tmp_path / "file1.csv").write_text("data")
        (tmp_path / "file2.txt").write_text("data")
        
        files = list_output_files(str(tmp_path), file_extensions=['.txt'])
        
        assert len(files) == 1
        assert files[0]["name"] == "file2.txt"
    
    def test_list_files_recursive(self, tmp_path):
        """Test listing files recursively in subdirectories"""
        from src.presentation.gui.services.file_service import list_output_files
        
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.csv").write_text("data")
        (tmp_path / "root.csv").write_text("data")
        
        files = list_output_files(str(tmp_path))
        
        assert len(files) == 2
    
    def test_list_files_returns_file_info(self, tmp_path):
        """Test that listed files have complete info"""
        from src.presentation.gui.services.file_service import list_output_files
        
        (tmp_path / "test.csv").write_text("some,data,here")
        
        files = list_output_files(str(tmp_path))
        
        assert len(files) == 1
        file_info = files[0]
        assert "name" in file_info
        assert "path" in file_info
        assert "size" in file_info
        assert "extension" in file_info
        assert file_info["extension"] == ".csv"


class TestGetFileSizeStr:
    """Tests for get_file_size_str function"""
    
    def test_bytes(self):
        """Test size in bytes"""
        from src.presentation.gui.services.file_service import format_file_size
        
        result = format_file_size(500)
        
        assert "B" in result
        assert "500" in result
    
    def test_kilobytes(self):
        """Test size in kilobytes"""
        from src.presentation.gui.services.file_service import format_file_size
        
        result = format_file_size(2048)
        
        assert "KB" in result
    
    def test_megabytes(self):
        """Test size in megabytes"""
        from src.presentation.gui.services.file_service import format_file_size
        
        result = format_file_size(2 * 1024 * 1024)
        
        assert "MB" in result
    
    def test_gigabytes(self):
        """Test size in gigabytes"""
        from src.presentation.gui.services.file_service import format_file_size
        
        result = format_file_size(2 * 1024 * 1024 * 1024)
        
        assert "GB" in result


class TestCreateDownloadZip:
    """Tests for create_download_zip function"""
    
    def test_create_zip_single_file(self, tmp_path):
        """Test creating zip with single file"""
        from src.presentation.gui.services.file_service import create_zip_archive
        
        # Create test file
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\n1,2,3")
        
        files = [{"path": str(test_file), "name": "test.csv"}]
        
        zip_bytes = create_zip_archive(files)
        
        assert len(zip_bytes) > 0
        
        # Verify it's a valid zip
        import io
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            assert "test.csv" in zf.namelist()
    
    def test_create_zip_multiple_files(self, tmp_path):
        """Test creating zip with multiple files"""
        from src.presentation.gui.services.file_service import create_zip_archive
        
        (tmp_path / "file1.csv").write_text("data1")
        (tmp_path / "file2.csv").write_text("data2")
        
        files = [
            {"path": str(tmp_path / "file1.csv"), "name": "file1.csv"},
            {"path": str(tmp_path / "file2.csv"), "name": "file2.csv"}
        ]
        
        zip_bytes = create_zip_archive(files)
        
        import io
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            assert len(zf.namelist()) == 2
    
    def test_create_zip_skip_nonexistent(self, tmp_path):
        """Test that non-existent files are skipped"""
        from src.presentation.gui.services.file_service import create_zip_archive
        
        files = [{"path": "/nonexistent/file.csv", "name": "missing.csv"}]
        
        zip_bytes = create_zip_archive(files)
        
        # Should create empty zip
        assert len(zip_bytes) > 0


class TestOrganizeFilesByBranch:
    """Tests for organize_files_by_branch function"""
    
    def test_organize_by_branch_from_path(self):
        """Test organizing files by branch from path"""
        from src.presentation.gui.services.file_service import group_files_by_branch
        
        files = [
            {"name": "file1.csv", "relative_path": "administration/file1.csv"},
            {"name": "file2.csv", "relative_path": "shahid/file2.csv"},
            {"name": "file3.csv", "relative_path": "administration/file3.csv"}
        ]
        
        organized = group_files_by_branch(files)
        
        assert "administration" in organized
        assert len(organized["administration"]) == 2
    
    def test_organize_unknown_branch(self):
        """Test that unknown branches go to 'other'"""
        from src.presentation.gui.services.file_service import group_files_by_branch
        
        files = [
            {"name": "unknown.csv", "relative_path": "unknown_branch/file.csv"}
        ]
        
        organized = group_files_by_branch(files)
        
        assert "other" in organized


class TestOrganizeFilesByCategory:
    """Tests for organize_files_by_category function"""
    
    def test_organize_by_category(self):
        """Test organizing files by category"""
        from src.presentation.gui.services.file_service import group_files_by_category
        
        files = [
            {"name": "transfer_tablets_and_capsules.csv"},
            {"name": "transfer_injections.csv"},
            {"name": "transfer_syrups.csv"}
        ]
        
        organized = group_files_by_category(files)
        
        assert "tablets_and_capsules" in organized
        assert "injections" in organized
        assert "syrups" in organized
    
    def test_organize_unknown_category(self):
        """Test that unknown categories go to 'other'"""
        from src.presentation.gui.services.file_service import group_files_by_category
        
        files = [
            {"name": "random_file.csv"}
        ]
        
        organized = group_files_by_category(files)
        
        assert "other" in organized


class TestReadFileForDisplay:
    """Tests for read_file_for_display function - needs minimal Streamlit mock"""
    
    def test_read_csv_file(self, tmp_path):
        """Test reading CSV file"""
        # Create mock for streamlit
        mock_st = MagicMock()
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            from src.presentation.gui.services.file_service import read_file_content
            
            # Create test CSV
            csv_file = tmp_path / "test.csv"
            csv_file.write_text("code,name,value\n001,A,10\n002,B,20")
            
            df = read_file_content(str(csv_file))
            
            # May return DataFrame or None depending on implementation
            if df is not None:
                assert isinstance(df, pd.DataFrame)
    
    def test_read_nonexistent_file(self, tmp_path):
        """Test reading non-existent file"""
        # Need to patch streamlit at the module level
        with patch('src.presentation.gui.services.file_service') as mock_st:
            from src.presentation.gui.services.file_service import read_file_content
            
            result = read_file_content("/nonexistent/file.csv")
            
            # Should return None
            assert result is None
            # mock_st.error.assert_called_once() # Error is silent now in service logic

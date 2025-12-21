"""Tests for file handling utility functions"""

import os
import tempfile
import shutil
from pathlib import Path

import pytest

from src.shared.utils.file_handler import (
    ensure_directory_exists,
    get_file_path,
    get_excel_files,
    get_csv_files,
    get_latest_file
)


class TestEnsureDirectoryExists:
    """Tests for ensure_directory_exists function"""
    
    def test_create_new_directory(self, temp_directory):
        """Test creating a new directory"""
        new_dir = os.path.join(temp_directory, 'new_folder')
        assert not os.path.exists(new_dir)
        
        ensure_directory_exists(new_dir)
        
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
    
    def test_existing_directory(self, temp_directory):
        """Test with existing directory (should not raise)"""
        # temp_directory already exists
        ensure_directory_exists(temp_directory)
        
        assert os.path.exists(temp_directory)
    
    def test_nested_directory(self, temp_directory):
        """Test creating nested directories"""
        nested_dir = os.path.join(temp_directory, 'level1', 'level2', 'level3')
        
        ensure_directory_exists(nested_dir)
        
        assert os.path.exists(nested_dir)


class TestGetFilePath:
    """Tests for get_file_path function"""
    
    def test_simple_path(self):
        """Test simple file path combination"""
        result = get_file_path('test.csv', '/home/user/data')
        
        assert result == '/home/user/data/test.csv'
    
    def test_path_with_trailing_slash(self):
        """Test directory with trailing slash"""
        result = get_file_path('test.csv', '/home/user/data/')
        
        # os.path.join handles trailing slashes
        assert 'test.csv' in result


class TestGetExcelFiles:
    """Tests for get_excel_files function"""
    
    def test_directory_with_excel_files(self, temp_directory):
        """Test getting Excel files from directory"""
        # Create test Excel files
        for i, ext in enumerate(['.xlsx', '.xls', '.xlsx']):
            Path(os.path.join(temp_directory, f'file{i}{ext}')).touch()
        
        # Create non-Excel files
        Path(os.path.join(temp_directory, 'file.csv')).touch()
        Path(os.path.join(temp_directory, 'file.txt')).touch()
        
        result = get_excel_files(temp_directory)
        
        assert len(result) == 3
        assert all(f.endswith(('.xlsx', '.xls')) for f in result)
    
    def test_empty_directory(self, temp_directory):
        """Test empty directory returns empty list"""
        result = get_excel_files(temp_directory)
        
        assert result == []
    
    def test_nonexistent_directory(self):
        """Test non-existent directory returns empty list"""
        result = get_excel_files('/nonexistent/path')
        
        assert result == []
    
    def test_sorted_results(self, temp_directory):
        """Test that results are sorted"""
        for name in ['c_file.xlsx', 'a_file.xlsx', 'b_file.xlsx']:
            Path(os.path.join(temp_directory, name)).touch()
        
        result = get_excel_files(temp_directory)
        
        assert result == sorted(result)


class TestGetCsvFiles:
    """Tests for get_csv_files function"""
    
    def test_directory_with_csv_files(self, temp_directory):
        """Test getting CSV files from directory"""
        # Create test CSV files
        for i in range(3):
            Path(os.path.join(temp_directory, f'file{i}.csv')).touch()
        
        # Create non-CSV files
        Path(os.path.join(temp_directory, 'file.xlsx')).touch()
        
        result = get_csv_files(temp_directory)
        
        assert len(result) == 3
        assert all(f.endswith('.csv') for f in result)
    
    def test_empty_directory(self, temp_directory):
        """Test empty directory returns empty list"""
        result = get_csv_files(temp_directory)
        
        assert result == []
    
    def test_nonexistent_directory(self):
        """Test non-existent directory returns empty list"""
        result = get_csv_files('/nonexistent/path')
        
        assert result == []
    
    def test_case_insensitive(self, temp_directory):
        """Test that extension matching is case insensitive"""
        Path(os.path.join(temp_directory, 'file.CSV')).touch()
        Path(os.path.join(temp_directory, 'file2.Csv')).touch()
        
        result = get_csv_files(temp_directory)
        
        assert len(result) == 2


class TestGetLatestFile:
    """Tests for get_latest_file function"""
    
    def test_get_latest_by_modification_time(self, temp_directory):
        """Test getting latest file by modification time"""
        import time
        
        # Create files with different modification times
        file1 = os.path.join(temp_directory, 'old_file.csv')
        file2 = os.path.join(temp_directory, 'new_file.csv')
        
        Path(file1).touch()
        time.sleep(0.1)  # Small delay
        Path(file2).touch()
        
        result = get_latest_file(temp_directory)
        
        assert result == 'new_file.csv'
    
    def test_filter_by_extension(self, temp_directory):
        """Test filtering by extension"""
        import time
        
        # Create older CSV file
        Path(os.path.join(temp_directory, 'old.csv')).touch()
        time.sleep(0.1)
        # Create newer Excel file
        Path(os.path.join(temp_directory, 'new.xlsx')).touch()
        
        # Should return the CSV even though Excel is newer
        result = get_latest_file(temp_directory, extension='.csv')
        
        assert result == 'old.csv'
    
    def test_empty_directory(self, temp_directory):
        """Test empty directory returns None"""
        result = get_latest_file(temp_directory)
        
        assert result is None
    
    def test_nonexistent_directory(self):
        """Test non-existent directory returns None"""
        result = get_latest_file('/nonexistent/path')
        
        assert result is None
    
    def test_no_matching_extension(self, temp_directory):
        """Test no files matching extension returns None"""
        Path(os.path.join(temp_directory, 'file.xlsx')).touch()
        
        result = get_latest_file(temp_directory, extension='.csv')
        
        assert result is None

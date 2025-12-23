import os
import shutil
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.shared.utils.archiver.cleanup import delete_directory_contents
from src.app.pipeline.step_11.balance_reader import get_branch_balances
from src.app.pipeline.step_10.shortage.writers.orchestrator import generate_all_files

class TestArchiverCleanupRobustness:
    def test_delete_directory_contents_handles_errors(self, tmp_path):
        """Test that delete_directory_contents handles deletion errors gracefully."""
        # Create a directory with a file
        test_dir = tmp_path / "cleanup_test"
        test_dir.mkdir()
        file_path = test_dir / "protected.txt"
        file_path.write_text("protected content")
        
        # Mock os.remove to raise an exception
        with patch('os.remove', side_effect=PermissionError("Permission denied")):
            # Should not raise exception
            delete_directory_contents(str(test_dir))
            # Verify the file still exists (since deletion failed)
            assert file_path.exists()

class TestStep11BalanceReaderRobustness:
    def test_get_branch_balances_non_existent_dir(self):
        """Test get_branch_balances with a non-existent directory."""
        result = get_branch_balances("/non/existent/path", "branch1")
        assert result == {}

    def test_get_branch_balances_empty_csv(self, tmp_path):
        """Test get_branch_balances with an empty CSV file."""
        branch_dir = tmp_path / "branch1"
        branch_dir.mkdir()
        csv_path = branch_dir / "latest.csv"
        csv_path.write_text("من: 01/01/2024\ncode,balance\n") # Just header
        
        with patch('src.app.pipeline.step_11.balance_reader.get_latest_file', return_value="latest.csv"):
            result = get_branch_balances(str(tmp_path), "branch1")
            assert result == {}

    def test_get_branch_balances_missing_columns(self, tmp_path):
        """Test get_branch_balances with missing required columns."""
        branch_dir = tmp_path / "branch1"
        branch_dir.mkdir()
        csv_path = branch_dir / "latest.csv"
        csv_path.write_text("code,wrong_column\n101,50\n")
        
        with patch('src.app.pipeline.step_11.balance_reader.get_latest_file', return_value="latest.csv"):
            result = get_branch_balances(str(tmp_path), "branch1")
            assert result == {}

class TestStep10ShortageWriterIntegration:
    def test_generate_all_files_creates_structure(self, tmp_path):
        """Test that generate_all_files correctly orchestrates file generation."""
        csv_dir = tmp_path / "csv"
        excel_dir = tmp_path / "excel"
        
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['P1', 'P2'],
            'needed_quantity': [10, 20],
            'company': ['C1', 'C2']
        })
        
        # Mocking get_product_categories to return a predictable list
        with patch('src.app.pipeline.step_10.shortage.writers.orchestrator.get_product_categories', return_value=['Cat1']):
            with patch('src.app.pipeline.step_10.shortage.writers.csv_writer.generate_category_files', return_value={'Cat1': 'path1'}):
                with patch('src.app.pipeline.step_10.shortage.writers.csv_writer.create_combined_file', return_value='combined_path'):
                    generated_files, categories = generate_all_files(
                        df, False, "", str(csv_dir), str(excel_dir)
                    )
                    
                    assert 'Cat1' in generated_files
                    assert 'all' in generated_files
                    assert categories == ['Cat1']
                    assert csv_dir.exists()
                    assert excel_dir.exists()

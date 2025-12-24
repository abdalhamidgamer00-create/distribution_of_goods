import sys
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.presentation.gui.components.file_grouping import (
    get_key_from_label,
    group_files_by_branch,
    group_files_by_source_target
)

class TestGetKeyFromLabel:
    """Tests for get_key_from_label function"""
    
    def test_get_none_for_all(self):
        """Test returning None for 'الكل' (All) label"""
        labels = {"branch1": "فرع 1", "branch2": "فرع 2"}
        assert get_key_from_label("الكل", labels) is None
        
    def test_get_existing_key(self):
        """Test returning key for existing label"""
        labels = {"branch1": "فرع 1", "branch2": "فرع 2"}
        assert get_key_from_label("فرع 1", labels) == "branch1"
        assert get_key_from_label("فرع 2", labels) == "branch2"
        
    def test_get_none_for_invalid(self):
        """Test returning None for invalid label"""
        labels = {"branch1": "فرع 1"}
        assert get_key_from_label("فرع غير موجود", labels) is None

class TestGroupFilesByBranch:
    """Tests for group_files_by_branch function"""
    
    def test_group_empty_list(self):
        """Test grouping an empty list of files"""
        assert group_files_by_branch([]) == {}
        
    def test_group_single_branch(self):
        """Test grouping files belonging to a single branch"""
        files = [
            {"name": "file1.csv", "branch": "A"},
            {"name": "file2.csv", "branch": "A"}
        ]
        expected = {"A": [{"name": "file1.csv", "branch": "A"}, {"name": "file2.csv", "branch": "A"}]}
        assert group_files_by_branch(files) == expected
        
    def test_group_multiple_branches(self):
        """Test grouping files across multiple branches"""
        files = [
            {"name": "file1.csv", "branch": "A"},
            {"name": "file2.csv", "branch": "B"},
            {"name": "file3.csv", "branch": "A"}
        ]
        result = group_files_by_branch(files)
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1
        
    def test_group_with_unknown_branch(self):
        """Test grouping files with missing branch key"""
        files = [{"name": "file1.csv"}]
        expected = {"unknown": [{"name": "file1.csv"}]}
        assert group_files_by_branch(files) == expected

class TestGroupFilesBySourceTarget:
    """Tests for group_files_by_source_target function"""
    
    def test_group_by_pairs(self):
        """Test grouping files by source/target branch pairs"""
        files = [
            {"name": "f1.csv", "source_branch": "A", "target_branch": "B"},
            {"name": "f2.csv", "source_branch": "A", "target_branch": "B"},
            {"name": "f3.csv", "source_branch": "B", "target_branch": "A"}
        ]
        result = group_files_by_source_target(files)
        assert len(result[("A", "B")]) == 2
        assert len(result[("B", "A")]) == 1
        
    def test_group_with_missing_branches(self):
        """Test grouping with missing source or target info"""
        files = [{"name": "f1.csv"}]
        result = group_files_by_source_target(files)
        assert result[("unknown", "unknown")] == [{"name": "f1.csv"}]

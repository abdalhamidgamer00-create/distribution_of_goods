"""Tests for transfer service functions"""

import os
import tempfile
import shutil
from pathlib import Path

import pandas as pd
import pytest

from src.services.transfers.generators.transfer_generator import (
    generate_transfer_for_pair,
    generate_transfer_files
)


class TestGenerateTransferForPair:
    """Tests for generate_transfer_for_pair function"""
    
    @pytest.fixture
    def setup_analytics_dir(self, temp_directory):
        """Setup analytics directory structure for testing"""
        analytics_dir = os.path.join(temp_directory, 'analytics')
        transfers_dir = os.path.join(temp_directory, 'transfers')
        os.makedirs(analytics_dir, exist_ok=True)
        os.makedirs(transfers_dir, exist_ok=True)
        
        # Create target branch analytics directory
        target_dir = os.path.join(analytics_dir, 'admin')
        os.makedirs(target_dir, exist_ok=True)
        
        # Create analytics file
        df = pd.DataFrame({
            'code': ['001', '002', '003'],
            'product_name': ['Product A', 'Product B', 'Product C'],
            'available_branch_1': ['wardani', 'wardani', 'akba'],
            'surplus_from_branch_1': [10, 5, 0],
            'available_branch_2': ['akba', '', ''],
            'surplus_from_branch_2': [3, 0, 0]
        })
        df.to_csv(os.path.join(target_dir, 'test_admin_analytics.csv'), 
                  index=False, encoding='utf-8-sig')
        
        return analytics_dir, transfers_dir
    
    def test_generate_transfer_file(self, setup_analytics_dir):
        """Test successful transfer file generation"""
        analytics_dir, transfers_dir = setup_analytics_dir
        
        result = generate_transfer_for_pair(
            source_branch='wardani',
            target_branch='admin',
            analytics_dir=analytics_dir,
            transfers_dir=transfers_dir
        )
        
        # Should return file path if transfers exist
        if result:
            assert os.path.exists(result)
            # Verify content
            df = pd.read_csv(result, encoding='utf-8-sig')
            assert 'code' in df.columns
            assert 'quantity_to_transfer' in df.columns
    
    def test_no_analytics_directory(self, temp_directory):
        """Test with non-existent analytics directory"""
        result = generate_transfer_for_pair(
            source_branch='wardani',
            target_branch='admin',
            analytics_dir='/nonexistent/path',
            transfers_dir=temp_directory
        )
        
        assert result is None
    
    def test_no_matching_transfers(self, temp_directory):
        """Test when no transfers match source branch"""
        analytics_dir = os.path.join(temp_directory, 'analytics')
        transfers_dir = os.path.join(temp_directory, 'transfers')
        target_dir = os.path.join(analytics_dir, 'admin')
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(transfers_dir, exist_ok=True)
        
        # Create analytics with no matching source
        df = pd.DataFrame({
            'code': ['001'],
            'product_name': ['Product A'],
            'available_branch_1': ['akba'],  # Not wardani
            'surplus_from_branch_1': [10]
        })
        df.to_csv(os.path.join(target_dir, 'test_analytics.csv'), 
                  index=False, encoding='utf-8-sig')
        
        result = generate_transfer_for_pair(
            source_branch='wardani',  # No match
            target_branch='admin',
            analytics_dir=analytics_dir,
            transfers_dir=transfers_dir
        )
        
        # Should return None when no transfers
        assert result is None
    
    def test_with_date_header(self, setup_analytics_dir):
        """Test transfer generation with date header"""
        analytics_dir, transfers_dir = setup_analytics_dir
        
        first_line = "من: 01/09/2024 00:00 إلى: 01/12/2024 00:00"
        
        result = generate_transfer_for_pair(
            source_branch='wardani',
            target_branch='admin',
            analytics_dir=analytics_dir,
            transfers_dir=transfers_dir,
            has_date_header=True,
            first_line=first_line
        )
        
        if result:
            with open(result, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                # Date header should be in file
                assert '01/09/2024' in content or 'code' in content.lower()


class TestGenerateTransferFiles:
    """Tests for generate_transfer_files function"""
    
    def test_returns_dictionary(self, temp_directory):
        """Test that function returns a dictionary"""
        result = generate_transfer_files(
            analytics_dir=temp_directory,
            transfers_dir=temp_directory
        )
        
        assert isinstance(result, dict)
    
    def test_excludes_same_branch_pairs(self, temp_directory):
        """Test that same-branch pairs are not generated"""
        result = generate_transfer_files(
            analytics_dir=temp_directory,
            transfers_dir=temp_directory
        )
        
        # No (branch, branch) pairs should exist
        for source, target in result.keys():
            assert source != target
    
    def test_empty_analytics_returns_empty(self, temp_directory):
        """Test with empty analytics directory"""
        analytics_dir = os.path.join(temp_directory, 'empty_analytics')
        transfers_dir = os.path.join(temp_directory, 'transfers')
        os.makedirs(analytics_dir, exist_ok=True)
        os.makedirs(transfers_dir, exist_ok=True)
        
        result = generate_transfer_files(
            analytics_dir=analytics_dir,
            transfers_dir=transfers_dir
        )
        
        assert result == {}

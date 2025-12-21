"""Tests for CLI input_handler module"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestGetUserChoice:
    """Tests for get_user_choice function"""
    
    def test_get_user_choice_returns_input(self):
        """Test that get_user_choice returns user input"""
        from src.app.cli.handlers.input_handler import get_user_choice
        
        with patch('builtins.input', return_value='5'):
            result = get_user_choice()
            
            assert result == '5'
    
    def test_get_user_choice_strips_whitespace(self):
        """Test that get_user_choice strips whitespace"""
        from src.app.cli.handlers.input_handler import get_user_choice
        
        with patch('builtins.input', return_value='  3  '):
            result = get_user_choice()
            
            assert result == '3'


class TestGetFileSelectionMode:
    """Tests for get_file_selection_mode function"""
    
    def test_select_specific_file(self):
        """Test selecting specific file option (1)"""
        from src.app.cli.handlers.input_handler import get_file_selection_mode
        
        with patch('builtins.input', return_value='1'):
            result = get_file_selection_mode()
            
            assert result is False  # False means select specific
    
    def test_use_latest_file(self):
        """Test using latest file option (2)"""
        from src.app.cli.handlers.input_handler import get_file_selection_mode
        
        with patch('builtins.input', return_value='2'):
            result = get_file_selection_mode()
            
            assert result is True  # True means use latest
    
    def test_invalid_option(self):
        """Test invalid option returns None"""
        from src.app.cli.handlers.input_handler import get_file_selection_mode
        
        with patch('builtins.input', return_value='3'):
            result = get_file_selection_mode()
            
            assert result is None
    
    def test_empty_input(self):
        """Test empty input returns None"""
        from src.app.cli.handlers.input_handler import get_file_selection_mode
        
        with patch('builtins.input', return_value=''):
            result = get_file_selection_mode()
            
            assert result is None

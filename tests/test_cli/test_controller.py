"""Tests for CLI controller module"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestControllerFunctions:
    """Tests for CLI controller functions"""
    
    def test_is_exit_choice_with_exit(self):
        """Test is_exit_choice returns True for exit choice"""
        from src.app.cli.core.controller import is_exit_choice
        from src.app.cli.core.cli_constants import EXIT_CHOICE
        
        assert is_exit_choice(EXIT_CHOICE) is True
    
    def test_is_exit_choice_with_non_exit(self):
        """Test is_exit_choice returns False for non-exit choice"""
        from src.app.cli.core.controller import is_exit_choice
        
        assert is_exit_choice("1") is False
        assert is_exit_choice("5") is False
        assert is_exit_choice("") is False
    
    def test_is_all_steps_choice_with_all(self):
        """Test is_all_steps_choice returns True for all steps choice"""
        from src.app.cli.core.controller import is_all_steps_choice
        from src.app.cli.core.cli_constants import ALL_STEPS_CHOICE_OFFSET
        
        assert is_all_steps_choice(str(ALL_STEPS_CHOICE_OFFSET)) is True
    
    def test_is_all_steps_choice_with_other(self):
        """Test is_all_steps_choice returns False for other choices"""
        from src.app.cli.core.controller import is_all_steps_choice
        
        assert is_all_steps_choice("1") is False
        assert is_all_steps_choice("5") is False
    
    def test_is_valid_step_choice_valid(self):
        """Test is_valid_step_choice returns True for valid step IDs"""
        from src.app.cli.core.controller import is_valid_step_choice
        
        # Steps 1-11 are valid
        assert is_valid_step_choice("1") is True
        assert is_valid_step_choice("5") is True
        assert is_valid_step_choice("11") is True
    
    def test_is_valid_step_choice_invalid(self):
        """Test is_valid_step_choice returns False for invalid step IDs"""
        from src.app.cli.core.controller import is_valid_step_choice
        
        assert is_valid_step_choice("0") is False
        assert is_valid_step_choice("15") is False
        assert is_valid_step_choice("abc") is False
        assert is_valid_step_choice("") is False


class TestHandleUserChoice:
    """Tests for handle_user_choice function"""
    
    def test_handle_exit_choice(self):
        """Test handle_user_choice returns False for exit"""
        from src.app.cli.core.controller import handle_user_choice
        from src.app.cli.core.cli_constants import EXIT_CHOICE
        
        result = handle_user_choice(EXIT_CHOICE)
        
        assert result is False
    
    def test_handle_invalid_choice(self):
        """Test handle_user_choice returns True for invalid choice"""
        from src.app.cli.core.controller import handle_user_choice
        
        result = handle_user_choice("invalid")
        
        # Should continue (return True) after showing error
        assert result is True
    
    def test_handle_valid_step_choice(self):
        """Test handle_user_choice with valid step"""
        from src.app.cli.core.controller import handle_user_choice
        
        with patch('src.app.cli.core.controller.execute_step_with_dependencies') as mock_exec:
            mock_exec.return_value = True
            
            result = handle_user_choice("1")
            
            assert result is True
            mock_exec.assert_called_once_with("1")
    
    def test_handle_all_steps_choice(self):
        """Test handle_user_choice with all steps"""
        from src.app.cli.core.controller import handle_user_choice
        from src.app.cli.core.cli_constants import ALL_STEPS_CHOICE_OFFSET
        
        with patch('src.app.cli.core.controller.execute_all_steps') as mock_exec:
            mock_exec.return_value = True
            
            result = handle_user_choice(str(ALL_STEPS_CHOICE_OFFSET))
            
            assert result is True
            mock_exec.assert_called_once()

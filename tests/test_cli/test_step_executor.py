"""Tests for CLI step_executor module"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestFindStepById:
    """Tests for find_step_by_id function"""
    
    def test_find_existing_step(self):
        """Test finding an existing step"""
        from src.app.cli.executors.step_executor import find_step_by_id
        
        step = find_step_by_id("1")
        
        assert step is not None
        assert step.id == "1"
    
    def test_find_nonexistent_step(self):
        """Test finding a non-existent step"""
        from src.app.cli.executors.step_executor import find_step_by_id
        
        step = find_step_by_id("999")
        
        assert step is None
    
    def test_find_all_valid_steps(self):
        """Test that all steps 1-11 can be found"""
        from src.app.cli.executors.step_executor import find_step_by_id
        
        for i in range(1, 12):
            step = find_step_by_id(str(i))
            assert step is not None, f"Step {i} should exist"


class TestValidateStepFunction:
    """Tests for validate_step_function function"""
    
    def test_validate_with_callable(self):
        """Test validation with callable function"""
        from src.app.cli.executors.step_executor import validate_step_function
        
        step = MagicMock()
        step.function = lambda: True
        
        assert validate_step_function(step) is True
    
    def test_validate_without_function(self):
        """Test validation without function"""
        from src.app.cli.executors.step_executor import validate_step_function
        
        # Create a mock without 'function' attribute
        step = MagicMock(spec=[])
        
        assert validate_step_function(step) is False
    
    def test_validate_with_non_callable(self):
        """Test validation with non-callable"""
        from src.app.cli.executors.step_executor import validate_step_function
        
        step = MagicMock()
        step.function = "not a function"
        
        assert validate_step_function(step) is False


class TestExecuteSingleStep:
    """Tests for execute_single_step function"""
    
    def test_execute_success(self):
        """Test successful step execution"""
        from src.app.cli.executors.step_executor import execute_single_step
        
        mock_func = MagicMock(return_value=True)
        step = MagicMock()
        step.id = "test"
        step.function = mock_func
        
        result = execute_single_step(step, use_latest_file=True)
        
        assert result is True
        mock_func.assert_called_once_with(use_latest_file=True)
    
    def test_execute_failure(self):
        """Test failed step execution"""
        from src.app.cli.executors.step_executor import execute_single_step
        
        mock_func = MagicMock(return_value=False)
        step = MagicMock()
        step.id = "test"
        step.function = mock_func
        
        result = execute_single_step(step, use_latest_file=False)
        
        assert result is False
    
    def test_execute_with_exception(self):
        """Test step execution with exception"""
        from src.app.cli.executors.step_executor import execute_single_step
        
        mock_func = MagicMock(side_effect=Exception("Test error"))
        step = MagicMock()
        step.id = "test"
        step.function = mock_func
        
        result = execute_single_step(step)
        
        assert result is False
    
    def test_execute_without_valid_function(self):
        """Test execution without valid function"""
        from src.app.cli.executors.step_executor import execute_single_step
        
        step = MagicMock()
        step.id = "test"
        step.function = None
        
        result = execute_single_step(step)
        
        assert result is False


class TestExecuteStep:
    """Tests for execute_step function"""
    
    def test_execute_invalid_step(self):
        """Test executing invalid step ID"""
        from src.app.cli.executors.step_executor import execute_step
        
        result = execute_step("999")
        
        assert result is False
    
    def test_execute_valid_step(self):
        """Test executing valid step"""
        from src.app.cli.executors.step_executor import execute_step
        
        with patch('src.app.cli.executors.step_executor.execution.execute_single_step') as mock_exec:
            mock_exec.return_value = True
            
            result = execute_step("1")
            
            assert result is True


class TestExecuteStepWithDependencies:
    """Tests for execute_step_with_dependencies function"""
    
    def test_invalid_step_id(self):
        """Test with invalid step ID"""
        from src.app.cli.executors.step_executor import execute_step_with_dependencies
        
        result = execute_step_with_dependencies("abc")
        
        assert result is False
    
    def test_step_not_found(self):
        """Test with step that doesn't exist"""
        from src.app.cli.executors.step_executor import execute_step_with_dependencies
        
        # Step 0 doesn't exist
        result = execute_step_with_dependencies("0")
        
        assert result is False
    
    def test_execute_with_dependencies_success(self):
        """Test successful execution with dependencies"""
        from src.app.cli.executors.step_executor import execute_step_with_dependencies
        
        with patch('src.app.cli.executors.step_executor.sequence.execute_single_step') as mock_exec:
            mock_exec.return_value = True
            
            result = execute_step_with_dependencies("2")
            
            # Should call execute_single_step for steps 1 and 2
            assert mock_exec.call_count == 2
            assert result is True
    
    def test_execute_with_dependencies_failure(self):
        """Test execution stops on failure"""
        from src.app.cli.executors.step_executor import execute_step_with_dependencies
        
        with patch('src.app.cli.executors.step_executor.sequence.execute_single_step') as mock_exec:
            # First step fails
            mock_exec.return_value = False
            
            result = execute_step_with_dependencies("3")
            
            # Should stop after first failure
            assert mock_exec.call_count == 1
            assert result is False

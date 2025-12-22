"""Tests for GUI step_runner module using use_streamlit=False"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestGetStepInfo:
    """Tests for get_step_info function"""
    
    def test_get_existing_step_info(self):
        """Test getting info for existing step"""
        from src.app.gui.utils.step_runner import get_step_info
        
        info = get_step_info("1")
        
        assert info is not None
        assert info["id"] == "1"
        assert "name" in info
        assert "description" in info
    
    def test_get_nonexistent_step_info(self):
        """Test getting info for non-existent step"""
        from src.app.gui.utils.step_runner import get_step_info
        
        info = get_step_info("999")
        
        assert info is None
    
    def test_get_all_step_infos(self):
        """Test getting info for all steps 1-11"""
        from src.app.gui.utils.step_runner import get_step_info
        
        for i in range(1, 12):
            info = get_step_info(str(i))
            assert info is not None, f"Step {i} info should exist"
            assert info["id"] == str(i)


class TestGetAllSteps:
    """Tests for get_all_steps function"""
    
    def test_get_all_steps_returns_list(self):
        """Test that get_all_steps returns a list"""
        from src.app.gui.utils.step_runner import get_all_steps
        
        steps = get_all_steps()
        
        assert isinstance(steps, list)
        assert len(steps) == 11  # 11 steps
    
    def test_get_all_steps_has_translations(self):
        """Test that steps have translated names"""
        from src.app.gui.utils.step_runner import get_all_steps
        
        steps = get_all_steps()
        
        for step in steps:
            assert "id" in step
            assert "name" in step
            assert "description" in step


class TestRunStep:
    """Tests for run_step function with use_streamlit=False"""
    
    def test_run_nonexistent_step(self):
        """Test running a non-existent step"""
        from src.app.gui.utils.step_runner import run_step
        
        success, message = run_step("999", use_streamlit=False)
        
        assert success is False
        assert "غير موجودة" in message or "999" in message
    
    def test_run_step_success(self):
        """Test running a step successfully"""
        from src.app.gui.utils.step_runner import run_step
        from src.app.pipeline.steps import AVAILABLE_STEPS
        
        # Mock the step function
        original_func = AVAILABLE_STEPS[0]["function"]
        AVAILABLE_STEPS[0]["function"] = MagicMock(return_value=True)
        
        try:
            success, message = run_step("1", use_streamlit=False)
            
            assert success is True
            assert "نجاح" in message or "Success" in message.lower() or "✓" in message or "1" in message
        finally:
            AVAILABLE_STEPS[0]["function"] = original_func
    
    def test_run_step_failure(self):
        """Test running a step that fails"""
        from src.app.gui.utils.step_runner import run_step
        from src.app.pipeline.steps import AVAILABLE_STEPS
        
        # Mock the step function to return False
        original_func = AVAILABLE_STEPS[0]["function"]
        AVAILABLE_STEPS[0]["function"] = MagicMock(return_value=False)
        
        try:
            success, message = run_step("1", use_streamlit=False)
            
            assert success is False
        finally:
            AVAILABLE_STEPS[0]["function"] = original_func
    
    def test_run_step_exception(self):
        """Test running a step that throws exception"""
        from src.app.gui.utils.step_runner import run_step
        from src.app.pipeline.steps import AVAILABLE_STEPS
        
        # Mock the step function to throw exception
        original_func = AVAILABLE_STEPS[0]["function"]
        AVAILABLE_STEPS[0]["function"] = MagicMock(side_effect=Exception("Test error"))
        
        try:
            success, message = run_step("1", use_streamlit=False)
            
            assert success is False
            assert "error" in message.lower() or "خطأ" in message
        finally:
            AVAILABLE_STEPS[0]["function"] = original_func


class TestRunStepWithDependencies:
    """Tests for run_step_with_dependencies function"""
    
    def test_invalid_step_id(self):
        """Test with invalid step ID"""
        from src.app.gui.utils.step_runner import run_step_with_dependencies
        
        success, message = run_step_with_dependencies("abc", use_streamlit=False)
        
        assert success is False
    
    def test_step_not_found(self):
        """Test with step number 0"""
        from src.app.gui.utils.step_runner import run_step_with_dependencies
        
        success, message = run_step_with_dependencies("0", use_streamlit=False)
        
        assert success is False
    
    def test_run_with_dependencies_success(self):
        """Test successful run with dependencies"""
        from src.app.gui.utils.step_runner import run_step_with_dependencies
        
        # Mock run_step to always succeed
        with patch('src.app.gui.utils.step_runner.run_step') as mock_run:
            mock_run.return_value = (True, "Success")
            
            success, message = run_step_with_dependencies("2", use_streamlit=False)
            
            # Should run steps 1 and 2
            assert mock_run.call_count == 2
            assert success is True
    
    def test_run_with_dependencies_failure(self):
        """Test that execution stops on failure"""
        from src.app.gui.utils.step_runner import run_step_with_dependencies
        
        # Mock run_step to fail
        with patch('src.app.gui.utils.step_runner.run_step') as mock_run:
            mock_run.return_value = (False, "Failed")
            
            success, message = run_step_with_dependencies("3", use_streamlit=False)
            
            # Should stop after first failure
            assert mock_run.call_count == 1
            assert success is False


class TestFindStepById:
    """Tests for _find_step_by_id helper function."""
    
    def test_find_existing_step(self):
        """
        WHAT: Return step dict for valid ID
        WHY: Core lookup functionality
        BREAKS: Steps not found even when they exist
        """
        from src.app.gui.utils.step_runner import _find_step_by_id
        
        step = _find_step_by_id("1")
        
        assert step is not None
        assert step["id"] == "1"
        assert "function" in step
    
    def test_find_nonexistent_step(self):
        """
        WHAT: Return None for invalid ID
        WHY: Graceful handling of bad input
        BREAKS: Exception on invalid step ID
        """
        from src.app.gui.utils.step_runner import _find_step_by_id
        
        step = _find_step_by_id("999")
        
        assert step is None
    
    def test_find_step_with_string_id(self):
        """
        WHAT: Handle string step IDs correctly
        WHY: IDs come from user input as strings
        BREAKS: Type mismatch errors
        """
        from src.app.gui.utils.step_runner import _find_step_by_id
        
        step = _find_step_by_id("11")
        
        assert step is not None
        assert step["id"] == "11"


class TestBuildStepInfo:
    """Tests for _build_step_info helper function."""
    
    def test_builds_complete_info(self):
        """
        WHAT: Return complete step info dict
        WHY: UI needs all step properties
        BREAKS: Missing properties in step cards
        """
        from src.app.gui.utils.step_runner import _build_step_info
        from src.app.pipeline.steps import AVAILABLE_STEPS
        
        step = AVAILABLE_STEPS[0]
        info = _build_step_info(step)
        
        assert "id" in info
        assert "name" in info
        assert "description" in info
        assert "function" in info
    
    def test_info_uses_translation(self):
        """
        WHAT: Use translated name when available
        WHY: Arabic UI requires translations
        BREAKS: English text in Arabic interface
        """
        from src.app.gui.utils.step_runner import _build_step_info
        from src.app.pipeline.steps import AVAILABLE_STEPS
        from src.app.gui.utils.translations import STEP_NAMES
        
        step = AVAILABLE_STEPS[0]
        info = _build_step_info(step)
        
        expected_name = STEP_NAMES.get(step["id"], step["name"])
        assert info["name"] == expected_name


class TestValidateStepId:
    """Tests for _validate_step_id helper function."""
    
    def test_valid_numeric_string(self):
        """
        WHAT: Accept numeric string IDs
        WHY: Step IDs are strings like "1", "11"
        BREAKS: Valid step IDs rejected
        """
        from src.app.gui.utils.step_runner import _validate_step_id
        
        valid, result = _validate_step_id("5")
        
        assert valid is True
        assert result == 5
    
    def test_invalid_non_numeric_string(self):
        """
        WHAT: Reject non-numeric strings
        WHY: Prevent invalid step lookups
        BREAKS: Crashes on bad input
        """
        from src.app.gui.utils.step_runner import _validate_step_id
        
        valid, result = _validate_step_id("abc")
        
        assert valid is False
        assert isinstance(result, str)  # Error message
    
    def test_handles_negative_numbers(self):
        """
        WHAT: Handle negative step numbers
        WHY: Edge case for input validation
        BREAKS: Unexpected behavior with negative numbers
        """
        from src.app.gui.utils.step_runner import _validate_step_id
        
        valid, result = _validate_step_id("-1")
        
        # Should parse but will fail later in lookup
        assert valid is True
        assert result == -1


class TestExecuteStepFunction:
    """Tests for _execute_step_function helper."""
    
    def test_returns_success_tuple_on_true(self):
        """
        WHAT: Return success tuple when function returns True
        WHY: Proper status propagation
        BREAKS: Wrong status messages
        """
        from src.app.gui.utils.step_runner import _execute_step_function
        
        mock_step = {"function": MagicMock(return_value=True)}
        
        success, message = _execute_step_function(mock_step, "Test Step", use_streamlit=False)
        
        assert success is True
        assert "نجاح" in message or "success" in message.lower() or "Test Step" in message
    
    def test_returns_failure_tuple_on_false(self):
        """
        WHAT: Return failure tuple when function returns False
        WHY: Proper error reporting
        BREAKS: Silent failures
        """
        from src.app.gui.utils.step_runner import _execute_step_function
        
        mock_step = {"function": MagicMock(return_value=False)}
        
        success, message = _execute_step_function(mock_step, "Test Step", use_streamlit=False)
        
        assert success is False
        assert "فشل" in message or "fail" in message.lower() or "Test Step" in message


class TestHandleRunStepError:
    """Tests for _handle_run_step_error helper."""
    
    def test_returns_error_tuple(self):
        """
        WHAT: Return error tuple with message
        WHY: Exception info needed for debugging
        BREAKS: Lost error details
        """
        from src.app.gui.utils.step_runner import _handle_run_step_error
        
        error = Exception("Test error message")
        
        success, message = _handle_run_step_error("Test Step", error, use_streamlit=False)
        
        assert success is False
        assert "Test error message" in message or "خطأ" in message


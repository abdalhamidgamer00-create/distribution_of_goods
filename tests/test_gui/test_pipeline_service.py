import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.app.gui.services.pipeline.pipeline_execution import (
    _find_step_by_id
)
from src.app.gui.services.pipeline.info import (
    _build_step_info
)
from src.app.gui.services.pipeline.sequences import (
    _validate_step_id
)
from src.app.gui.services.pipeline_service import (
    get_step_info,
    get_all_steps,
    run_single_step,
    get_steps_sequence
)


class TestGetStepInfo:
    """Tests for get_step_info function"""
    
    def test_get_existing_step_info(self):
        """Test getting info for existing step"""
        info = get_step_info("1")
        
        assert info is not None
        assert info.id == "1"
        assert hasattr(info, "name")
        assert hasattr(info, "description")
    
    def test_get_nonexistent_step_info(self):
        """Test getting info for non-existent step"""
        info = get_step_info("999")
        
        assert info is None
    
    def test_get_all_step_infos(self):
        """Test getting info for all steps 1-11"""
        for i in range(1, 12):
            info = get_step_info(str(i))
            assert info is not None, f"Step {i} info should exist"
            assert info.id == str(i)


class TestGetAllSteps:
    """Tests for get_all_steps function"""
    
    def test_get_all_steps_returns_list(self):
        """Test that get_all_steps returns a list"""
        steps = get_all_steps()
        
        assert isinstance(steps, list)
        assert len(steps) == 11  # 11 steps
    
    def test_get_all_steps_has_translations(self):
        """Test that steps have translated names"""
        steps = get_all_steps()
        
        for step in steps:
            assert hasattr(step, "id")
            assert hasattr(step, "name")
            assert hasattr(step, "description")


class TestRunStep:
    """Tests for run_step function with use_streamlit=False"""
    
    def test_run_nonexistent_step(self):
        """Test running a non-existent step"""
        success, message = run_single_step("999")
        
        assert success is False
        assert "غير موجودة" in message or "999" in message
    
    def test_run_step_success(self):
        """Test running a step successfully"""
        from src.app.pipeline.steps import AVAILABLE_STEPS
        
        # Create a mock step that mimics the structure but is mutable
        mock_step = MagicMock()
        mock_step.id = "1"
        mock_step.name = "Test Step"
        mock_step.function = MagicMock(return_value=True)

        with patch('src.app.gui.services.pipeline.pipeline_execution._find_step_by_id', return_value=mock_step):
            success, message = run_single_step("1")
            
            assert success is True
            assert "نجاح" in message or "Success" in message.lower() or "✓" in message or "1" in message
    
    def test_run_step_failure(self):
        """Test running a step that fails"""
        from src.app.pipeline.steps import AVAILABLE_STEPS
        
        # Create a mock step that mimics the structure but is mutable
        mock_step = MagicMock()
        mock_step.id = "1"
        mock_step.name = "Test Step"
        mock_step.function = MagicMock(return_value=False)

        with patch('src.app.gui.services.pipeline.pipeline_execution._find_step_by_id', return_value=mock_step):
            success, message = run_single_step("1")
            
            assert success is False
    
    def test_run_step_exception(self):
        """Test running a step that throws exception"""
        from src.app.pipeline.steps import AVAILABLE_STEPS
        
        # Create a mock step that mimics the structure but is mutable
        mock_step = MagicMock()
        mock_step.id = "1"
        mock_step.name = "Test Step"
        mock_step.function = MagicMock(side_effect=Exception("Test error"))

        with patch('src.app.gui.services.pipeline.pipeline_execution._find_step_by_id', return_value=mock_step):
            success, message = run_single_step("1")
            
            assert success is False
            assert "error" in message.lower() or "خطأ" in message


class TestGetStepsSequence:
    """Tests for get_steps_sequence function"""
    
    def test_invalid_step_id(self):
        """Test with invalid step ID"""
        success, message = get_steps_sequence("abc")
        
        assert success is False
    
    def test_step_not_found(self):
        """Test with step number 0"""
        success, message = get_steps_sequence("0")
        
        assert success is False
    
    def test_get_sequence_success(self):
        """Test successful retrieval of sequence"""
        success, steps = get_steps_sequence("2")
        
        assert success is True
        assert isinstance(steps, list)
        assert len(steps) == 2
        assert steps[0].id == "1"
        assert steps[1].id == "2"


class TestFindStepById:
    """Tests for _find_step_by_id helper function."""
    
    def test_find_existing_step(self):
        """
        WHAT: Return step dict for valid ID
        WHY: Core lookup functionality
        BREAKS: Steps not found even when they exist
        """
        step = _find_step_by_id("1")
        
        assert step is not None
        assert step.id == "1"
        assert step.function is not None
    
    def test_find_nonexistent_step(self):
        """
        WHAT: Return None for invalid ID
        WHY: Graceful handling of bad input
        BREAKS: Exception on invalid step ID
        """
        step = _find_step_by_id("999")
        
        assert step is None
    
    def test_find_step_with_string_id(self):
        """
        WHAT: Handle string step IDs correctly
        WHY: IDs come from user input as strings
        BREAKS: Type mismatch errors
        """
        step = _find_step_by_id("11")
        
        assert step is not None
        assert step.id == "11"


class TestBuildStepInfo:
    """Tests for _build_step_info helper function."""
    
    def test_builds_complete_info(self):
        """
        WHAT: Return complete step info dict
        WHY: UI needs all step properties
        BREAKS: Missing properties in step cards
        """
        from src.app.pipeline.steps import AVAILABLE_STEPS
        
        step = AVAILABLE_STEPS[0]
        info = _build_step_info(step)
        
        assert hasattr(info, "id")
        assert hasattr(info, "name")
        assert hasattr(info, "description")
        assert hasattr(info, "function")
    
    def test_info_uses_translation(self):
        """
        WHAT: Use translated name when available
        WHY: Arabic UI requires translations
        BREAKS: English text in Arabic interface
        """
        from src.app.pipeline.steps import AVAILABLE_STEPS
        from src.app.gui.utils.translations import STEP_NAMES
        
        step = AVAILABLE_STEPS[0]
        info = _build_step_info(step)
        
        expected_name = STEP_NAMES.get(step.id, step.name)
        assert info.name == expected_name


class TestValidateStepId:
    """Tests for _validate_step_id helper function."""
    
    def test_valid_numeric_string(self):
        """
        WHAT: Accept numeric string IDs
        WHY: Step IDs are strings like "1", "11"
        BREAKS: Valid step IDs rejected
        """
        valid, result = _validate_step_id("5")
        
        assert valid is True
        assert result == 5
    
    def test_invalid_non_numeric_string(self):
        """
        WHAT: Reject non-numeric strings
        WHY: Prevent invalid step lookups
        BREAKS: Crashes on bad input
        """
        valid, result = _validate_step_id("abc")
        
        assert valid is False
        assert isinstance(result, str)  # Error message
    
    def test_handles_negative_numbers(self):
        """
        WHAT: Handle negative step numbers
        WHY: Edge case for input validation
        BREAKS: Unexpected behavior with negative numbers
        """
        valid, result = _validate_step_id("-1")
        
        # Should parse but will fail later in lookup
        assert valid is True
        assert result == -1





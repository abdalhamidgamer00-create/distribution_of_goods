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

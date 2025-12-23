"""Tests for CLI display module."""

import pytest
from unittest.mock import patch, MagicMock

from src.app.cli.ui.display import display_menu, _display_step_item
from src.app.cli.core.constants import SEPARATOR, EXIT_CHOICE, ALL_STEPS_CHOICE_OFFSET


# ===================== _display_step_item Tests =====================

class TestDisplayStepItem:
    """Tests for _display_step_item function."""
    
    def test_displays_step_id_and_name(self, caplog):
        """
        WHAT: Display step ID and name
        WHY: Users need to identify steps
        BREAKS: Unclear menu options
        """
        step = {"id": "5", "name": "Test Step", "description": "Test description"}
        
        with caplog.at_level('INFO'):
            _display_step_item(step)
        
        assert "5" in caplog.text
        assert "Test Step" in caplog.text
    
    def test_displays_step_description(self, caplog):
        """
        WHAT: Display step description
        WHY: Users need to understand what step does
        BREAKS: No context for menu choices
        """
        step = {"id": "1", "name": "Archive", "description": "Archive previous output"}
        
        with caplog.at_level('INFO'):
            _display_step_item(step)
        
        assert "Archive previous output" in caplog.text


# ===================== display_menu Tests =====================

class TestDisplayMenu:
    """Tests for display_menu function."""
    
    def test_displays_menu_header(self, caplog):
        """
        WHAT: Display menu title
        WHY: Users need to know they're in menu
        BREAKS: Confusing interface
        """
        with caplog.at_level('INFO'):
            display_menu()
        
        assert "Menu" in caplog.text or "Project" in caplog.text
    
    def test_displays_all_steps(self, capsys):
        """
        WHAT: Display all available steps
        WHY: All options should be visible
        BREAKS: Missing menu options
        """
        from src.app.pipeline.steps import AVAILABLE_STEPS
        
        display_menu()
        
        captured = capsys.readouterr()
        
        # Should show at least some step numbers
        for i in range(1, min(5, len(AVAILABLE_STEPS) + 1)):
            assert str(i) in captured.out
    
    def test_displays_exit_option(self, caplog):
        """
        WHAT: Display exit option
        WHY: Users need to know how to exit
        BREAKS: No way to exit menu
        """
        with caplog.at_level('INFO'):
            display_menu()
        
        assert str(EXIT_CHOICE) in caplog.text
    
    def test_displays_all_steps_option(self, caplog):
        """
        WHAT: Display 'execute all' option
        WHY: Users can run all steps at once
        BREAKS: Missing batch execution option
        """
        with caplog.at_level('INFO'):
            display_menu()
        
        assert str(ALL_STEPS_CHOICE_OFFSET) in caplog.text or "all" in caplog.text.lower()
    
    def test_uses_separator(self, caplog):
        """
        WHAT: Use separator for visual clarity
        WHY: Menu should be well-formatted
        BREAKS: Hard to read menu
        """
        with caplog.at_level('INFO'):
            display_menu()
        
        # Should use some form of separator
        assert "=" in caplog.text or "-" in caplog.text


# ===================== Constants Tests =====================

class TestCliConstants:
    """Tests for CLI constants."""
    
    def test_separator_is_string(self):
        """
        WHAT: Separator should be a string
        WHY: Used for visual formatting
        BREAKS: Type error in display
        """
        assert isinstance(SEPARATOR, str)
        assert len(SEPARATOR) > 0
    
    def test_exit_choice_is_valid(self):
        """
        WHAT: Exit choice should be a valid option
        WHY: Must be parseable by input handler
        BREAKS: Cannot exit menu
        """
        assert EXIT_CHOICE is not None
    
    def test_all_steps_choice_is_valid(self):
        """
        WHAT: All steps choice should be valid
        WHY: Must be parseable by input handler
        BREAKS: Cannot run all steps
        """
        assert ALL_STEPS_CHOICE_OFFSET is not None

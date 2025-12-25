"""Unit tests for the centralized StepOrchestrator."""

import pytest
from src.application.pipeline.step_orchestrator import StepOrchestrator


class TestStepOrchestrator:
    """Tests for the StepOrchestrator class."""

    def test_get_isolated_sequence_for_archive_only(self):
        """Should return only Step 1 if requested."""
        sequence = StepOrchestrator.get_isolated_sequence("1")
        assert len(sequence) == 1
        assert sequence[0].id == "1"
        assert sequence[0].name == "Data Archiving"

    def test_get_isolated_sequence_with_archiving_prefix(self):
        """Should return [Step 1, Target Step] for any other step."""
        # Step 3 is usually Inventory Validation
        sequence = StepOrchestrator.get_isolated_sequence("3")
        assert len(sequence) == 2
        assert sequence[0].id == "1"
        assert sequence[1].id == "3"

    def test_get_isolated_sequence_for_step_10(self):
        """Should return [Step 1, Step 10] correctly."""
        sequence = StepOrchestrator.get_isolated_sequence("10")
        assert len(sequence) == 2
        assert sequence[0].id == "1"
        assert sequence[1].id == "10"

    def test_get_isolated_sequence_not_found(self):
        """Should return empty list for invalid step ID."""
        sequence = StepOrchestrator.get_isolated_sequence("999")
        assert sequence == []

    def test_find_step_success(self):
        """Should find a valid step."""
        step = StepOrchestrator.find_step("2")
        assert step is not None
        assert step.id == "2"

    def test_find_step_failure(self):
        """Should return None for invalid step."""
        step = StepOrchestrator.find_step("non_existent")
        assert step is None

    def test_get_sequence_up_to_step_3(self):
        """Should return steps 1, 2, 3 in order."""
        sequence = StepOrchestrator.get_sequence_up_to("3")
        assert len(sequence) == 3
        # Assuming typical IDs: 1, 2, 3
        ids = [s.id for s in sequence]
        assert ids == ["1", "2", "3"]

    def test_get_sequence_up_to_invalid_step(self):
        """Should return empty list for invalid target."""
        sequence = StepOrchestrator.get_sequence_up_to("invalid")
        assert sequence == []

    def test_get_previous_step_for_2(self):
        """Step 1 is previous to 2."""
        prev = StepOrchestrator.get_previous_step("2")
        assert prev is not None
        assert prev.id == "1"

    def test_get_previous_step_for_1(self):
        """No previous step for the first one."""
        prev = StepOrchestrator.get_previous_step("1")
        assert prev is None

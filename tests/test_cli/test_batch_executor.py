"""Comprehensive tests for batch_executor module.

Tests cover the batch step execution functionality which orchestrates
running all pipeline steps in sequence.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.app.cli.executors.batch_executor import (
    log_step_progress,
    _execute_and_track,
    execute_all_steps_batch,
    display_execution_summary,
    _run_steps_with_mode,
    execute_all_steps
)


# ===================== log_step_progress Tests =====================

class TestLogStepProgress:
    """Tests for log_step_progress function."""
    
    def test_logs_correct_format(self, caplog):
        """
        WHAT: Verify log format includes step number and name
        WHY: Users need clear progress indication
        BREAKS: Unclear progress during batch execution
        """
        step = {'id': 'step_1', 'name': 'Archive Output'}
        
        with caplog.at_level('INFO'):
            log_step_progress(step, 1, 11)
        
        # Should log step info
        assert '1/11' in caplog.text or 'step_1' in caplog.text
    
    def test_handles_first_step(self, caplog):
        """
        WHAT: Correctly log first step
        WHY: Edge case for starting batch
        BREAKS: Off-by-one errors in progress display
        """
        step = {'id': 'step_1', 'name': 'First Step'}
        
        with caplog.at_level('INFO'):
            log_step_progress(step, 1, 5)
        
        assert '1/5' in caplog.text or 'step_1' in caplog.text


# ===================== _execute_and_track Tests =====================

class TestExecuteAndTrack:
    """Tests for _execute_and_track function."""
    
    @patch('src.app.cli.executors.batch_executor.execute_single_step')
    def test_returns_success_on_successful_step(self, mock_execute):
        """
        WHAT: Return True when step succeeds
        WHY: Correct return value needed for batch control flow
        BREAKS: Batch stops incorrectly on success
        """
        mock_execute.return_value = True
        step = {'id': 'step_1', 'name': 'Test Step'}
        
        result = _execute_and_track(step, use_latest_file=True)
        
        assert result is True
        assert step['_last_result'] is True
    
    @patch('src.app.cli.executors.batch_executor.execute_single_step')
    def test_returns_false_on_failed_step(self, mock_execute):
        """
        WHAT: Return False when step fails
        WHY: Failures must be properly tracked
        BREAKS: Silent failures in batch execution
        """
        mock_execute.return_value = False
        step = {'id': 'step_1', 'name': 'Failing Step'}
        
        result = _execute_and_track(step, use_latest_file=True)
        
        assert result is False
        assert step['_last_result'] is False
    
    @patch('src.app.cli.executors.batch_executor.execute_single_step')
    def test_passes_file_selection_mode(self, mock_execute):
        """
        WHAT: Pass use_latest_file parameter to step executor
        WHY: File selection mode must be forwarded
        BREAKS: Steps always use wrong file selection
        """
        mock_execute.return_value = True
        step = {'id': 'step_1', 'name': 'Test Step'}
        
        _execute_and_track(step, use_latest_file=False)
        
        mock_execute.assert_called_once_with(step, False)


# ===================== execute_all_steps_batch Tests =====================

class TestExecuteAllStepsBatch:
    """Tests for execute_all_steps_batch function."""
    
    @patch('src.app.cli.executors.batch_executor._execute_and_track')
    @patch('src.app.cli.executors.batch_executor.log_step_progress')
    @patch('src.app.cli.executors.batch_executor.AVAILABLE_STEPS', [
        {'id': 'step_1', 'name': 'Step 1'},
        {'id': 'step_2', 'name': 'Step 2'}
    ])
    def test_returns_counts_all_success(self, mock_log, mock_execute):
        """
        WHAT: Return correct counts when all steps succeed
        WHY: Summary depends on accurate counts
        BREAKS: Wrong success rate displayed
        """
        mock_execute.return_value = True
        
        successful, total = execute_all_steps_batch(use_latest_file=True)
        
        assert successful == 2
        assert total == 2
    
    @patch('src.app.cli.executors.batch_executor._execute_and_track')
    @patch('src.app.cli.executors.batch_executor.log_step_progress')
    @patch('src.app.cli.executors.batch_executor.AVAILABLE_STEPS', [
        {'id': 'step_1', 'name': 'Step 1'},
        {'id': 'step_2', 'name': 'Step 2'},
        {'id': 'step_3', 'name': 'Step 3'}
    ])
    def test_returns_counts_partial_success(self, mock_log, mock_execute):
        """
        WHAT: Return correct counts when some steps fail
        WHY: Accurate tracking of failures
        BREAKS: Understated or overstated success count
        """
        mock_execute.side_effect = [True, False, True]
        
        successful, total = execute_all_steps_batch(use_latest_file=True)
        
        assert successful == 2
        assert total == 3
    
    @patch('src.app.cli.executors.batch_executor._execute_and_track')
    @patch('src.app.cli.executors.batch_executor.log_step_progress')
    @patch('src.app.cli.executors.batch_executor.AVAILABLE_STEPS', [])
    def test_handles_empty_steps_list(self, mock_log, mock_execute):
        """
        WHAT: Handle empty steps list gracefully
        WHY: Edge case that shouldn't crash
        BREAKS: Division by zero in summary
        """
        successful, total = execute_all_steps_batch(use_latest_file=True)
        
        assert successful == 0
        assert total == 0


# ===================== display_execution_summary Tests =====================

class TestDisplayExecutionSummary:
    """Tests for display_execution_summary function."""
    
    def test_logs_all_success_summary(self, caplog):
        """
        WHAT: Log summary for 100% success rate
        WHY: Summary should show perfect execution
        BREAKS: Confusing summary messages
        """
        with caplog.at_level('INFO'):
            display_execution_summary(10, 10)
        
        assert '10' in caplog.text
        assert '100' in caplog.text or '100.0' in caplog.text
    
    def test_logs_partial_success_summary(self, caplog):
        """
        WHAT: Log summary with failures
        WHY: Summary must show actual success rate
        BREAKS: User unaware of failures
        """
        with caplog.at_level('INFO'):
            display_execution_summary(7, 10)
        
        # Should mention success and failures
        assert '7' in caplog.text
        assert '10' in caplog.text
    
    def test_handles_zero_steps(self, caplog):
        """
        WHAT: Handle zero total steps without error
        WHY: Edge case that could cause division by zero
        BREAKS: Application crash on empty execution
        """
        with caplog.at_level('INFO'):
            # Should not raise exception
            display_execution_summary(0, 0)


# ===================== _run_steps_with_mode Tests =====================

class TestRunStepsWithMode:
    """Tests for _run_steps_with_mode function."""
    
    @patch('src.app.cli.executors.batch_executor.display_execution_summary')
    @patch('src.app.cli.executors.batch_executor.execute_all_steps_batch')
    def test_returns_true_on_all_success(self, mock_batch, mock_display):
        """
        WHAT: Return True when all steps succeed
        WHY: Caller needs to know overall status
        BREAKS: Wrong exit code for batch mode
        """
        mock_batch.return_value = (10, 10)
        
        result = _run_steps_with_mode(use_latest=True)
        
        assert result is True
    
    @patch('src.app.cli.executors.batch_executor.display_execution_summary')
    @patch('src.app.cli.executors.batch_executor.execute_all_steps_batch')
    def test_returns_false_on_any_failure(self, mock_batch, mock_display):
        """
        WHAT: Return False when any step fails
        WHY: Partial failure is still failure
        BREAKS: Silent failures in automated scripts
        """
        mock_batch.return_value = (9, 10)
        
        result = _run_steps_with_mode(use_latest=False)
        
        assert result is False
    
    @patch('src.app.cli.executors.batch_executor.execute_all_steps_batch')
    def test_handles_exception_gracefully(self, mock_batch):
        """
        WHAT: Return False on exception
        WHY: Exceptions shouldn't crash the entire application
        BREAKS: Unhandled exception in batch mode
        """
        mock_batch.side_effect = Exception("Test error")
        
        result = _run_steps_with_mode(use_latest=True)
        
        assert result is False


# ===================== execute_all_steps Tests =====================

class TestExecuteAllSteps:
    """Tests for execute_all_steps function."""
    
    @patch('src.app.cli.executors.batch_executor._run_steps_with_mode')
    @patch('src.app.cli.executors.batch_executor.get_file_selection_mode')
    def test_runs_with_user_selection(self, mock_get_mode, mock_run):
        """
        WHAT: Use user's file selection preference
        WHY: User choice should be respected
        BREAKS: Always uses wrong file selection
        """
        mock_get_mode.return_value = True
        mock_run.return_value = True
        
        result = execute_all_steps()
        
        mock_run.assert_called_once_with(True)
        assert result is True
    
    @patch('src.app.cli.executors.batch_executor._run_steps_with_mode')
    @patch('src.app.cli.executors.batch_executor.get_file_selection_mode')
    def test_returns_false_on_cancelled_selection(self, mock_get_mode, mock_run):
        """
        WHAT: Return False when user cancels file selection
        WHY: Cancellation should exit gracefully
        BREAKS: Null pointer on cancelled selection
        """
        mock_get_mode.return_value = None
        
        result = execute_all_steps()
        
        assert result is False
        mock_run.assert_not_called()

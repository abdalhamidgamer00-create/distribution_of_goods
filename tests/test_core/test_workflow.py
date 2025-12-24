import pytest
from unittest.mock import MagicMock, patch
from src.app.core.workflow import PipelineManager
from src.domain.exceptions.pipeline_exceptions import PrerequisiteNotFoundError


class TestPipelineManager:
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()

    @pytest.fixture
    def manager(self, mock_repo):
        return PipelineManager(repository=mock_repo)

    def test_run_service_raises_and_rescues(self, manager):
        """Verify that run_service rescues missing prerequisites."""
        manager._is_data_present = MagicMock(side_effect=[False, True, True])
        manager._services["ingest"] = MagicMock()
        manager._services["ingest"].execute.return_value = True
        manager._services["normalize"] = MagicMock()
        manager._services["normalize"].execute.return_value = True

        # normalize depends on ingest
        result = manager.run_service("normalize")

        assert result is True
        assert manager._services["ingest"].execute.called
        assert manager._services["normalize"].execute.called

    def test_run_service_recursion_guard(self, manager):
        """Verify that recursion guard prevents infinite loops on persistent failures."""
        # Always report data as missing, causing repeated rescue attempts
        manager._is_data_present = MagicMock(return_value=False)
        manager._services["ingest"] = MagicMock()
        manager._services["ingest"].execute.return_value = True
        
        # This would recurse infinitely without the guard
        result = manager.run_service("normalize")

        assert result is False
        # Should call ingest once, then fail the rescue check
        assert manager._services["ingest"].execute.call_count == 1

    def test_workflow_state_provider(self, manager):
        """Verify that get_workflow_state returns current status."""
        manager._is_data_present = MagicMock(return_value=True)
        state = manager.get_workflow_state()
        
        assert state.step_results["ingest"].is_success is True
        assert state.step_results["normalize"].is_success is True

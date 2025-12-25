"""Pipeline orchestration for distribution logistics."""

import os
from datetime import datetime
from typing import Dict, Optional
from src.shared.utility.logging_utils import get_logger
from src.infrastructure.repositories.base.pandas_repository import (
    PandasDataRepository
)
from src.shared.config.paths import (
    RENAMED_CSV_DIR, ANALYTICS_DIR, SURPLUS_DIR, 
    SHORTAGE_DIR, TRANSFERS_CSV_DIR, TRANSFERS_ROOT_DIR
)
from src.domain.models.pipeline import StepResult, PipelineState
from src.domain.exceptions.pipeline_exceptions import PrerequisiteNotFoundError
from src.shared.utility.telemetry import execution_timer
from src.application.pipeline.pipeline_config import PipelineConfig
logger = get_logger(__name__)

class PipelineManager:
    """Orchestrates use cases with performance tracking."""

    def __init__(self, repository=None):
        self._repository = repository or self._create_default_repository()
        self._config = PipelineConfig()
        self._services = self._config.initialize_services(self._repository)
        self._contracts = self._config.define_contracts()
        self._dependencies = self._config.define_dependencies()
        self._history: Dict[str, StepResult] = {}

    def run_all(self, use_latest_file: bool = None) -> bool:
        """Executes the complete distribution sequence in order."""
        sequence = self._config.get_full_sequence(use_latest_file)
        for name, args in sequence:
            if not self.run_service(name, **args):
                return False
        return True

    def run_service(self, service_name: str, **kwargs) -> bool:
        """Executes a service with timing and rescue logic."""
        try:
            self._resolve_prerequisites(service_name, **kwargs)
            with execution_timer(service_name):
                success = self._services[service_name].execute(**kwargs)
            self._record_result(service_name, success, "Success")
            return success
        except PrerequisiteNotFoundError as error:
            return self._handle_rescue(service_name, error, **kwargs)
        except Exception as error:
            self._record_result(service_name, False, str(error))
            return False
    def get_workflow_state(self) -> PipelineState:
        """Returns the current collective health of the pipeline."""
        results = {}
        for name in self._services:
            is_present = self._is_data_present(name)
            if is_present:
                results[name] = StepResult(
                    name, True, datetime.now(), "Data on disk"
                )
            elif name in self._history:
                results[name] = self._history[name]
        return PipelineState(step_results=results)

    def _resolve_prerequisites(self, name: str, **kwargs) -> None:
        """Verifies all required upstream data artifacts exist."""
        for prerequisite in self._dependencies.get(name, []):
            if not self._is_data_present(prerequisite):
                raise PrerequisiteNotFoundError(name, prerequisite)

    def _is_data_present(self, name: str) -> bool:
        """Matches service output against its data contract."""
        if name not in self._contracts:
            return True
        path = self._contracts[name].output_path
        from src.shared.utility import file_handler
        return os.path.exists(path) and (
            file_handler.has_files_in_directory(path)
        )

    def _handle_rescue(self, name, error, **kwargs) -> bool:
        """Attempts to resolve a missing prerequisite."""
        logger.warning(f"Rescuing: {error}")
        res_name = error.missing_prerequisite
        if not (self.run_service(res_name, **kwargs) and 
                self._is_data_present(res_name)):
            return False
        return self.run_service(name, **kwargs)

    def _record_result(self, name: str, success: bool, message: str) -> None:
        """Stores the outcome of a service execution in history."""
        self._history[name] = StepResult(name, success, datetime.now(), message)

    def _create_default_repository(self) -> PandasDataRepository:
        """Initializes the standard repository for the manager."""
        from src.application.factories.repository_factory import RepositoryFactory
        return RepositoryFactory.create_pandas_repository()

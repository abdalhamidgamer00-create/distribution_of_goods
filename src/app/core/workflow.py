from datetime import datetime
from typing import List, Dict, Tuple, Optional
from src.shared.utils.logging_utils import get_logger
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.shared.config.paths import (
    RENAMED_CSV_DIR, ANALYTICS_DIR, SURPLUS_DIR, 
    SHORTAGE_DIR, TRANSFERS_CSV_DIR, INPUT_CSV_DIR,
    TRANSFERS_ROOT_DIR, COMBINED_DIR
)
from src.domain.models.pipeline import PipelineContract, StepResult, PipelineState
from src.domain.exceptions.pipeline_exceptions import PrerequisiteNotFoundError, ServiceExecutionError

# Use Case Imports
from src.application.use_cases.archive_data import ArchiveData
from src.application.use_cases.ingest_data import IngestData
from src.application.use_cases.validate_inventory import ValidateInventory
from src.application.use_cases.analyze_sales import AnalyzeSales
from src.application.use_cases.normalize_schema import NormalizeSchema
from src.application.use_cases.segment_branches import SegmentBranches
from src.application.use_cases.optimize_transfers import OptimizeTransfers
from src.application.use_cases.classify_transfers import ClassifyTransfers
from src.application.use_cases.report_surplus import ReportSurplus
from src.application.use_cases.report_shortage import ReportShortage
from src.application.use_cases.consolidate_transfers import ConsolidateTransfers

logger = get_logger(__name__)


class PipelineManager:
    """Orchestrates the execution of use cases with formal data contracts."""

    def __init__(self, repository=None):
        self._repository = repository or self._create_default_repository()
        self._services = self._initialize_services()
        self._contracts = self._define_contracts()
        self._dependencies = self._define_dependencies()
        self._execution_history: Dict[str, StepResult] = {}

    def run_all(self, use_latest_file: bool = None) -> bool:
        """Executes the complete distribution sequence."""
        sequence = self._get_full_sequence(use_latest_file)
        for name, arguments in sequence:
            if not self.run_service(name, **arguments):
                return False
        return True

    def run_service(self, service_name: str, **kwargs) -> bool:
        """Runs a service, resolving prerequisites with recursion guards."""
        try:
            self._resolve_prerequisites(service_name, **kwargs)
            success = self._services[service_name].execute(**kwargs)
            self._record_result(service_name, success, "Success" if success else "Fail")
            return success
        except PrerequisiteNotFoundError as error:
            logger.warning(f"Rescuing: {error}")
            if not self.run_service(error.missing_prerequisite, **kwargs):
                return False
            if not self._is_data_present(error.missing_prerequisite):
                logger.error(f"Rescue failed for {error.missing_prerequisite}")
                return False
            return self.run_service(service_name, **kwargs)
        except Exception as error:
            self._record_result(service_name, False, str(error))
            return False

    def get_workflow_state(self) -> PipelineState:
        """Returns the current state and health of all pipeline steps."""
        results = {}
        for service_name in self._services:
            if self._is_data_present(service_name):
                results[service_name] = StepResult(
                    service_name=service_name, is_success=True,
                    timestamp=datetime.now(), message="Data on disk"
                )
            elif service_name in self._execution_history:
                results[service_name] = self._execution_history[service_name]
        return PipelineState(step_results=results)

    def _resolve_prerequisites(self, service_name: str, **kwargs) -> None:
        """Checks formal contracts; raises PrerequisiteNotFoundError if violated."""
        prerequisites = self._dependencies.get(service_name, [])
        for prerequisite in prerequisites:
            if not self._is_data_present(prerequisite):
                raise PrerequisiteNotFoundError(service_name, prerequisite)

    def _is_data_present(self, service_name: str) -> bool:
        """Verifies if a service's output satisfies its defined contract."""
        if service_name not in self._contracts:
            return True
        contract = self._contracts[service_name]
        return self._verify_contract_path(contract.output_path, contract.output_type)

    def _verify_contract_path(self, path: str, check_type: str) -> bool:
        """Verifies disk content against contract, with recursive support."""
        import os
        from src.shared.utils.file_handler import has_files_in_directory
        if not os.path.exists(path):
            return False
            
        # Recursive check needed for nested output structures
        if check_type in ["csv", "any"]:
            return has_files_in_directory(path)

        return False

    def _record_result(self, name: str, success: bool, message: str) -> None:
        """Persists the result of a step in the execution history."""
        self._execution_history[name] = StepResult(
            service_name=name, is_success=success,
            timestamp=datetime.now(), message=message
        )

    def _create_default_repository(self) -> PandasDataRepository:
        """Creates repo with central path configuration."""
        return PandasDataRepository(
            input_dir=RENAMED_CSV_DIR, output_dir=TRANSFERS_ROOT_DIR,
            analytics_dir=ANALYTICS_DIR, surplus_dir=SURPLUS_DIR,
            shortage_dir=SHORTAGE_DIR, transfers_dir=TRANSFERS_CSV_DIR
        )

    def _initialize_services(self) -> dict:
        """Wire up all use cases with the shared repository."""
        repo = self._repository
        return {
            "archive": ArchiveData(), "ingest": IngestData(),
            "validate": ValidateInventory(), "analyze": AnalyzeSales(),
            "normalize": NormalizeSchema(), "segment": SegmentBranches(repo),
            "optimize": OptimizeTransfers(repo), "classify": ClassifyTransfers(repo),
            "report_surplus": ReportSurplus(repo), "report_shortage": ReportShortage(repo),
            "consolidate": ConsolidateTransfers(repo)
        }

    def _define_contracts(self) -> Dict[str, PipelineContract]:
        """Definitions of expected outputs for each pipeline step."""
        return {
            "ingest": PipelineContract("ingest", INPUT_CSV_DIR, "csv", "Raw Data"),
            "normalize": PipelineContract("normalize", RENAMED_CSV_DIR, "csv", "Normalized"),
            "segment": PipelineContract("segment", ANALYTICS_DIR, "any", "Segments"),
            "optimize": PipelineContract("optimize", TRANSFERS_ROOT_DIR, "csv", "Transfers"),
            "report_surplus": PipelineContract("report_surplus", SURPLUS_DIR, "csv", "Surplus")
        }

    def _define_dependencies(self) -> dict:
        """Logical ordering and prerequisites of the workflow."""
        return {
            "validate": ["ingest"], "analyze": ["ingest"],
            "normalize": ["ingest"], "segment": ["normalize"],
            "optimize": ["segment"], "classify": ["optimize"],
            "report_surplus": ["segment"], "report_shortage": ["segment"],
            "consolidate": ["optimize", "report_surplus"]
        }

    def _get_full_sequence(self, use_latest: bool) -> list:
        """Standard sequence for a complete automated run."""
        params = {"use_latest_file": use_latest}
        return [
            ("archive", {}), ("ingest", params), ("validate", params),
            ("analyze", params), ("normalize", params), ("segment", {}),
            ("optimize", {}), ("classify", {}), ("report_surplus", {}),
            ("report_shortage", {}), ("consolidate", {})
        ]

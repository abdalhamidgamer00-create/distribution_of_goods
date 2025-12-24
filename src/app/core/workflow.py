"""Orchestration logic for the distribution workflow."""

from src.shared.utils.logging_utils import get_logger
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.shared.config.paths import (
    RENAMED_CSV_DIR, ANALYTICS_DIR, SURPLUS_DIR, 
    SHORTAGE_DIR, TRANSFERS_CSV_DIR, INPUT_CSV_DIR,
    COMBINED_DIR
)

# Import domain services (Use Cases)
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
    """Orchestrates the execution of use cases in the distribution pipeline."""

    def __init__(self, repository=None):
        self._repository = repository or self._create_default_repository()
        self._services = self._initialize_services()
        self._deps = self._define_dependencies()

    def run_all(self, use_latest_file: bool = None) -> bool:
        """Executes the complete distribution workflow."""
        logger.info("Starting full distribution workflow...")
        sequence = self._get_full_sequence(use_latest_file)
        
        for name, args in sequence:
            logger.info(f"--- Running Service: {name.upper()} ---")
            if not self._services[name].execute(**args):
                logger.error(f"Service {name} failed. Aborting pipeline.")
                return False
        
        logger.info("=" * 50)
        logger.info("✓ Full distribution workflow completed successfully!")
        return True

    def run_service(self, service_name: str, **kwargs) -> bool:
        """Runs a specific service by name, resolving dependencies if missing."""
        if service_name not in self._services:
            logger.error(f"Unknown service: {service_name}")
            return False
            
        if not self._check_and_resolve_deps(service_name, **kwargs):
            return False

        return self._services[service_name].execute(**kwargs)

    def _create_default_repository(self) -> PandasDataRepository:
        """Creates a repository with standard paths."""
        return PandasDataRepository(
            input_dir=RENAMED_CSV_DIR,
            output_dir=ANALYTICS_DIR,
            analytics_dir=ANALYTICS_DIR,
            surplus_dir=SURPLUS_DIR,
            shortage_dir=SHORTAGE_DIR,
            transfers_dir=TRANSFERS_CSV_DIR
        )

    def _initialize_services(self) -> dict:
        """Initializes all use cases with their dependencies."""
        repo = self._repository
        return {
            "archive": ArchiveData(), "ingest": IngestData(),
            "validate": ValidateInventory(), "analyze": AnalyzeSales(),
            "normalize": NormalizeSchema(), "segment": SegmentBranches(repo),
            "optimize": OptimizeTransfers(repo), "classify": ClassifyTransfers(repo),
            "report_surplus": ReportSurplus(repo), "report_shortage": ReportShortage(repo),
            "consolidate": ConsolidateTransfers(repo)
        }

    def _define_dependencies(self) -> dict:
        """Defines the relationship between different services."""
        return {
            "validate": ["ingest"], "analyze": ["ingest"],
            "normalize": ["ingest"], "segment": ["normalize"],
            "optimize": ["segment"], "classify": ["optimize"],
            "report_surplus": ["segment"], "report_shortage": ["segment"],
            "consolidate": ["optimize", "report_surplus"]
        }

    def _get_full_sequence(self, use_latest: bool) -> list:
        """Returns the complete sequence of steps for a full run."""
        args = {"use_latest_file": use_latest}
        return [
            ("archive", {}), ("ingest", args), ("validate", args),
            ("analyze", args), ("normalize", args), ("segment", {}),
            ("optimize", {}), ("classify", {}), ("report_surplus", {}),
            ("report_shortage", {}), ("consolidate", {})
        ]

    def _check_and_resolve_deps(self, name: str, **kwargs) -> bool:
        """Ensures all prerequisites for a service are met."""
        if name not in self._deps:
            return True

        for dep in self._deps[name]:
            if not self._is_data_present(dep):
                logger.warning(f"Prerequisite '{dep}' missing for '{name}'.")
                if not self.run_service(dep, **kwargs):
                    return False
        return True

    def _is_data_present(self, name: str) -> bool:
        """Checks if the output data of a service exists on disk."""
        import os
        from src.shared.utils.file_handler import get_csv_files
        
        paths = {
            "ingest": INPUT_CSV_DIR, "normalize": RENAMED_CSV_DIR,
            "segment": ANALYTICS_DIR, "optimize": TRANSFERS_CSV_DIR,
            "report_surplus": SURPLUS_DIR
        }

        path = paths.get(name)
        if not path or not os.path.exists(path):
            return False

        if name in ["ingest", "normalize", "optimize", "report_surplus"]:
            return len(get_csv_files(path)) > 0
        
        if name == "segment":
            return len(os.listdir(path)) > 0

        return True

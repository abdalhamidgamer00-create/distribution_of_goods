"""Orchestration logic for the distribution workflow."""

from src.shared.utils.logging_utils import get_logger
from src.infrastructure.persistence.pandas_repository import PandasDataRepository

# Import domain services
from src.app.services.distribution.archivator import ArchivatorService
from src.app.services.distribution.ingestion import IngestionService
from src.app.services.distribution.validation import ValidationService
from src.app.services.distribution.analytics import AnalyticsService
from src.app.services.distribution.normalization import NormalizationService
from src.app.services.distribution.segmentation import SegmentationService
from src.app.services.distribution.engine import TransferOptimizer
from src.app.services.distribution.classification import TransferClassifier
from src.app.services.distribution.surplus import SurplusReporter
from src.app.services.distribution.shortage import ShortageReporter
from src.app.services.distribution.consolidation import ConsolidationService

logger = get_logger(__name__)

class PipelineManager:
    """Orchestrates the execution of domain services in the distribution pipeline."""

    def __init__(self, repository=None):
        import os
        # Use default repository if none provided
        self._repository = repository or PandasDataRepository(
            input_dir=os.path.join("data", "output", "converted", "renamed"),
            output_dir=os.path.join("data", "output", "branches", "analytics")
        )
        
        # Initialize services
        self._services = {
            "archive": ArchivatorService(self._repository),
            "ingest": IngestionService(self._repository),
            "validate": ValidationService(self._repository),
            "analyze": AnalyticsService(self._repository),
            "normalize": NormalizationService(self._repository),
            "segment": SegmentationService(self._repository),
            "optimize": TransferOptimizer(self._repository),
            "classify": TransferClassifier(self._repository),
            "report_surplus": SurplusReporter(self._repository),
            "report_shortage": ShortageReporter(self._repository),
            "consolidate": ConsolidationService(self._repository)
        }

        # Define service dependencies
        self._deps = {
            "validate": ["ingest"],
            "analyze": ["ingest"],
            "normalize": ["ingest"],
            "segment": ["normalize"],
            "optimize": ["segment"],
            "classify": ["optimize"],
            "report_surplus": ["segment"],
            "report_shortage": ["segment"],
            "consolidate": ["optimize", "report_surplus"]
        }

    def run_all(self, use_latest_file: bool = None) -> bool:
        """Executes the complete distribution workflow."""
        logger.info("Starting full distribution workflow...")
        
        # Sequence of execution (logical dependencies)
        sequence = [
            ("archive", {}),
            ("ingest", {"use_latest_file": use_latest_file}),
            ("validate", {"use_latest_file": use_latest_file}),
            ("analyze", {"use_latest_file": use_latest_file}),
            ("normalize", {"use_latest_file": use_latest_file}),
            ("segment", {}),
            ("optimize", {}),
            ("classify", {}),
            ("report_surplus", {}),
            ("report_shortage", {}),
            ("consolidate", {})
        ]
        
        for service_name, kwargs in sequence:
            logger.info(f"--- Running Service: {service_name.upper()} ---")
            success = self._services[service_name].execute(**kwargs)
            if not success:
                logger.error(f"Service {service_name} failed. Aborting pipeline.")
                return False
        
        logger.info("=" * 50)
        logger.info("✓ Full distribution workflow completed successfully!")
        return True

    def run_service(self, service_name: str, **kwargs) -> bool:
        """Runs a specific service by name, resolving dependencies if missing."""
        use_latest = kwargs.get('use_latest_file')
        logger.info(f"PipelineManager: Running '{service_name}' (use_latest_file={use_latest})")
        
        if service_name not in self._services:
            logger.error(f"Unknown service: {service_name}")
            return False
            
        # Ensure dependencies exist before running
        if not self._check_and_resolve_deps(service_name, **kwargs):
            return False

        return self._services[service_name].execute(**kwargs)

    def _check_and_resolve_deps(self, service_name: str, **kwargs) -> bool:
        """Verifies if input data exists for a service, runs dependencies if not."""
        if service_name not in self._deps:
            return True

        logger.info(f"Checking dependencies for '{service_name}'...")
        for dep in self._deps[service_name]:
            data_present = self._is_data_present(dep)
            logger.info(f"  - Dependency '{dep}': {'FOUND' if data_present else 'MISSING'}")
            
            if not data_present:
                logger.warning(f"Required data for '{service_name}' missing. Resolving '{dep}'...")
                if not self.run_service(dep, **kwargs):
                    logger.error(f"Dependency resolution failed: '{dep}'")
                    return False
        return True

    def _is_data_present(self, service_name: str) -> bool:
        """Checks if the output data of a service is present on disk."""
        import os
        from src.shared.utils.file_handler import get_csv_files
        
        paths = {
            "ingest": os.path.join("data", "output", "converted", "csv"),
            "normalize": os.path.join("data", "output", "converted", "renamed"),
            "segment": os.path.join("data", "output", "branches", "analytics"),
            "optimize": os.path.join("data", "output", "transfers", "csv"),
            "report_surplus": os.path.join("data", "output", "remaining_surplus")
        }

        path = paths.get(service_name)
        if not path or not os.path.exists(path):
            logger.info(f"    - Path does not exist for '{service_name}': {path}")
            return False

        # Ingest and Normalize check for CSV files
        if service_name in ["ingest", "normalize", "optimize", "report_surplus"]:
            csv_files = get_csv_files(path)
            has_files = len(csv_files) > 0
            if not has_files:
                logger.info(f"    - No CSV files found in {path}")
            else:
                logger.info(f"    - Found {len(csv_files)} CSV files in {path}")
            return has_files
        
        # Segment checks for branch directories (just check if path exists and isn't empty)
        if service_name == "segment":
            contents = os.listdir(path)
            has_dirs = len(contents) > 0
            if not has_dirs:
                logger.info(f"    - No branch data found in {path}")
            else:
                logger.info(f"    - Found {len(contents)} items in {path}")
            return has_dirs

        return True

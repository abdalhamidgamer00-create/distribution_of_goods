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
        """Runs a specific service by name."""
        if service_name not in self._services:
            logger.error(f"Unknown service: {service_name}")
            return False
            
        return self._services[service_name].execute(**kwargs)

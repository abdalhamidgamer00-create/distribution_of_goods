"""Pipeline configuration for services, contracts, and dependencies."""

from typing import Dict
from src.domain.models.pipeline import PipelineContract
from src.shared.config.paths import (
    RENAMED_CSV_DIR, ANALYTICS_DIR, SURPLUS_DIR, 
    SHORTAGE_DIR, TRANSFERS_CSV_DIR, INPUT_CSV_DIR,
    TRANSFERS_ROOT_DIR
)

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


class PipelineConfig:
    """Provides service wiring, data contracts, and dependency graph."""

    @staticmethod
    def initialize_services(repository) -> dict:
        """Connects all use cases with the shared data repository."""
        return {
            "archive": ArchiveData(), 
            "ingest": IngestData(),
            "validate": ValidateInventory(), 
            "analyze": AnalyzeSales(),
            "normalize": NormalizeSchema(), 
            "segment": SegmentBranches(repository),
            "optimize": OptimizeTransfers(repository), 
            "classify": ClassifyTransfers(repository),
            "report_surplus": ReportSurplus(repository), 
            "report_shortage": ReportShortage(repository),
            "consolidate": ConsolidateTransfers(repository)
        }

    @staticmethod
    def define_contracts() -> Dict[str, PipelineContract]:
        """Maps each service to its expected output artifact contract."""
        return {
            "ingest": PipelineContract(
                "ingest", INPUT_CSV_DIR, "csv", "Raw Data"
            ),
            "normalize": PipelineContract(
                "normalize", RENAMED_CSV_DIR, "csv", "Normalized"
            ),
            "segment": PipelineContract(
                "segment", ANALYTICS_DIR, "any", "Segments"
            ),
            "optimize": PipelineContract(
                "optimize", TRANSFERS_ROOT_DIR, "csv", "Transfers"
            ),
            "report_surplus": PipelineContract(
                "report_surplus", SURPLUS_DIR, "csv", "Surplus"
            )
        }

    @staticmethod
    def define_dependencies() -> dict:
        """Defines the directed graph of service prerequisites."""
        return {
            "validate": ["ingest"], "analyze": ["ingest"],
            "normalize": ["ingest"], "segment": ["normalize"],
            "optimize": ["segment"], "classify": ["optimize"],
            "report_surplus": ["segment"], "report_shortage": ["segment"],
            "consolidate": ["optimize", "report_surplus"]
        }

    @staticmethod
    def get_full_sequence(use_latest_file: bool) -> list:
        """Returns the standard sequence for a full pipeline run."""
        parameters = {"use_latest_file": use_latest_file}
        return [
            ("archive", {}), ("ingest", parameters), ("validate", parameters),
            ("analyze", parameters), ("normalize", parameters), 
            ("segment", {}), ("optimize", {}), ("classify", {}), 
            ("report_surplus", {}), ("report_shortage", {}), 
            ("consolidate", {})
        ]

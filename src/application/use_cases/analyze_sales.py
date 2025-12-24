"""Use case for performing sales analysis and generating reports."""

import os
from src.shared.utils.logging_utils import get_logger
from src.core.domain.analysis.sales_analyzer import analyze_csv_data
from src.shared.reporting.report_generator import generate_report
from src.infrastructure.services.file_selector import FileSelectorService
from src.shared.config.paths import INPUT_CSV_DIR

logger = get_logger(__name__)


class AnalyzeSales:
    """Orchestrates the sales analysis and reporting process."""

    def __init__(self):
        self._input_directory = INPUT_CSV_DIR

    def execute(self, use_latest_file: bool = True, **kwargs) -> bool:
        """Selects a CSV file and generates a sales performance report."""
        csv_name = FileSelectorService.select_csv_file(
            self._input_directory, use_latest=use_latest_file
        )
        
        if not csv_name:
            logger.error("No CSV file found for analysis.")
            return False

        csv_path = os.path.join(self._input_directory, csv_name)
        logger.info("Analyzing sales data: %s", csv_name)
        logger.info("-" * 50)

        return self._run_analysis_safely(csv_path, csv_name)

    def _run_analysis_safely(self, csv_path: str, filename: str) -> bool:
        """Runs domain analysis logic and handles potential failures."""
        try:
            results = analyze_csv_data(csv_path)
            report = generate_report(results, filename)
            
            # Log the report as intended by the system
            logger.info("\n%s", report)
            return True
        except Exception as error:
            logger.exception(f"AnalyzeSales use case failed: {error}")
            return False

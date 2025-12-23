"""Use case for performing sales analysis and generating reports."""

import os
from src.shared.utils.logging_utils import get_logger
from src.core.domain.analysis.sales_analyzer import analyze_csv_data
from src.shared.reporting.report_generator import generate_report
from src.infrastructure.services.file_selector import FileSelectorService

logger = get_logger(__name__)

class AnalyzeSales:
    """Orchestrates the sales analysis and reporting process."""

    def __init__(self):
        self._input_directory = os.path.join("data", "output", "converted", "csv")

    def execute(self, use_latest_file: bool = True, **kwargs) -> bool:
        """
        Selects a CSV file and generates a sales performance report.
        
        Args:
            use_latest_file: If True, automatically selects the newest file.
            **kwargs: Additional arguments.
        """
        csv_filename = FileSelectorService.select_csv_file(self._input_directory, use_latest=use_latest_file)
        
        if not csv_filename:
            logger.error("No CSV file found for analysis in %s", self._input_directory)
            return False

        csv_path = os.path.join(self._input_directory, csv_filename)
        logger.info("Analyzing sales data: %s", csv_filename)
        logger.info("-" * 50)

        try:
            analysis_results = analyze_csv_data(csv_path)
            report_text = generate_report(analysis_results, csv_filename)
            
            # Log the report (this is what the legacy service did)
            logger.info("\n%s", report_text)
            
            return True
        except Exception as e:
            logger.exception(f"AnalyzeSales use case failed: {e}")
            return False

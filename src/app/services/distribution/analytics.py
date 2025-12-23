"""Service for performing sales analysis on ingested data."""

import os
from src.shared.utils.file_handler import get_file_path, get_csv_files
from src.core.domain.analysis.sales_analyzer import analyze_csv_data
from src.shared.reporting.report_generator import generate_report
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.utils.file_selector import select_csv_file
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class AnalyticsService:
    """Manages the generation of sales performance and trend reports."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._converted_dir = os.path.join("data", "output", "converted", "csv")

    def execute(self, use_latest_file: bool = None) -> bool:
        """Analyzes CSV data and generates a detailed report."""
        csv_files = get_csv_files(self._converted_dir)
        
        if not csv_files:
            logger.error(f"No CSV files found in {self._converted_dir}")
            return False
        
        try:
            csv_file = select_csv_file(self._converted_dir, csv_files, use_latest_file)
            csv_path = get_file_path(csv_file, self._converted_dir)
            
            logger.info(f"Analyzing {csv_file}...")
            logger.info("-" * 50)
            
            analysis = analyze_csv_data(csv_path)
            report = generate_report(analysis, csv_file)
            logger.info(f"\n{report}")
            
            return True
        except Exception as e:
            logger.exception(f"AnalyticsService failed: {e}")
            return False

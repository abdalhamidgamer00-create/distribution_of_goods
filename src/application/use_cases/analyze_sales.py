"""Use case for performing sales analysis and generating reports."""

import os
from src.shared.utility.logging_utils import get_logger
from src.domain.services.analysis.sales_analyzer import analyze_csv_data
from src.shared.reporting.report_generator import generate_report
from src.infrastructure.adapters.file_selector import FileSelectorService
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
            
            # Save results to CSV (Standardize with 'csv' subfolder)
            from src.shared.config.paths import SALES_REPORT_DIR
            import pandas as pd
            
            # --- CSV Export ---
            csv_dir = os.path.join(SALES_REPORT_DIR, "csv")
            os.makedirs(csv_dir, exist_ok=True)
            csv_report_path = os.path.join(csv_dir, f"analysis_{filename}")
            
            # --- Excel Export ---
            excel_dir = os.path.join(SALES_REPORT_DIR, "excel")
            os.makedirs(excel_dir, exist_ok=True)
            excel_filename = f"analysis_{filename.replace('.csv', '')}.xlsx"
            excel_report_path = os.path.join(excel_dir, excel_filename)
            
            # Flatten results and save
            df = pd.DataFrame([results])
            # If date_range is a dict, flatten it or convert to string
            if 'date_range' in df.columns:
                df['date_range'] = df['date_range'].apply(lambda x: str(x) if x else "")
                
            df.to_csv(csv_report_path, index=False, encoding='utf-8-sig')
            df.to_excel(excel_report_path, index=False)
            
            logger.info("Saved analysis reports: CSV=%s, Excel=%s", csv_report_path, excel_report_path)

            # Log text report
            report = generate_report(results, filename)
            logger.info("\n%s", report)
            return True
        except Exception as error:
            logger.exception(f"AnalyzeSales use case failed: {error}")
            return False

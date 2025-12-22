"""Step 4: Sales Analysis handler"""

import os
from src.shared.utils.file_handler import get_file_path, get_csv_files
from src.core.domain.analysis.sales_analyzer import analyze_csv_data
from src.shared.reporting.report_generator import generate_report
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.utils.file_selector import select_csv_file

logger = get_logger(__name__)


def _execute_analysis(csv_path: str, csv_file: str) -> bool:
    """Execute the analysis and generate report."""
    logger.info("Analyzing %s...", csv_file)
    logger.info("-" * 50)
    
    analysis = analyze_csv_data(csv_path)
    report = generate_report(analysis, csv_file)
    logger.info("\n%s", report)
    return True


def _process_analysis(output_dir: str, csv_files: list, use_latest_file: bool) -> bool:
    """Process analysis with error handling."""
    try:
        csv_file = select_csv_file(output_dir, csv_files, use_latest_file)
        csv_path = get_file_path(csv_file, output_dir)
        return _execute_analysis(csv_path, csv_file)
    except ValueError as e:
        logger.error("Error: %s", e)
        return False
    except Exception as e:
        logger.exception("Error during analysis: %s", e)
        return False


def step_4_sales_analysis(use_latest_file: bool = None) -> bool:
    """Step 4: Generate sales analysis report"""
    output_dir = os.path.join("data", "output", "converted", "csv")
    csv_files = get_csv_files(output_dir)
    
    if not csv_files:
        logger.error("No CSV files found in %s", output_dir)
        return False
    
    return _process_analysis(output_dir, csv_files, use_latest_file)


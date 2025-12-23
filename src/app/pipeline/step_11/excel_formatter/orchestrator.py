"""Orchestrator for Excel formatting process."""

from typing import List, Dict
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_11.excel_formatter import converter

logger = get_logger(__name__)


def process_single_csv(file_info: dict, excel_output_dir: str) -> str:
    """Process a single CSV file and return Excel path or None."""
    csv_path = file_info.get('path')
    # Use os.path logic here or let converter handle it? 
    # The original called os.path.exists here.
    import os
    if not csv_path or not os.path.exists(csv_path):
        return None
        
    try:
        return converter.convert_single_file(csv_path, excel_output_dir)
    except Exception as error:
        logger.warning(f"Error converting {csv_path}: {error}")
        return None


def convert_to_excel_with_formatting(
    csv_files: List[Dict], excel_output_dir: str
) -> List[str]:
    """Convert CSV files to Excel with conditional formatting."""
    return [
        path for path in (
            process_single_csv(file_info, excel_output_dir) 
            for file_info in csv_files
        ) 
        if path
    ]

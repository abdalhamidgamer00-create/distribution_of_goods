"""Step 2: Convert Excel to CSV handler"""

import os
import re
from datetime import datetime
from src.services.conversion.converters.excel_to_csv import convert_excel_to_csv
from src.shared.utils.file_handler import ensure_directory_exists, get_file_path, get_excel_files
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.utils.file_selector import select_excel_file

logger = get_logger(__name__)


def _get_excel_file_from_streamlit(excel_files: list) -> str:
    """Try to get Excel file from Streamlit session state."""
    try:
        import streamlit as st
        if hasattr(st, 'session_state') and 'selected_file' in st.session_state:
            excel_file = st.session_state['selected_file']
            logger.info("Using Streamlit selected file: %s", excel_file)
            return excel_file if excel_file in excel_files else None
    except (ImportError, RuntimeError): pass
    return None


def _generate_output_filename(excel_file: str) -> str:
    """Generate output CSV filename with timestamp."""
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(excel_file)[0]
    base_name_clean = re.sub(r'_\d{8}_\d{6}', '', base_name)
    return f"{base_name_clean}_{date_str}.csv"


def _select_excel_file_source(excel_files: list, input_dir: str, use_latest_file: bool):
    """Select Excel file from Streamlit or selector."""
    excel_file = _get_excel_file_from_streamlit(excel_files)
    if not excel_file:
        excel_file = select_excel_file(input_dir, excel_files, use_latest_file)
    return excel_file


def _log_conversion_result(success: bool, converted_dir: str) -> None:
    """Log conversion result."""
    if success:
        logger.info("Conversion successful! File saved to: %s", converted_dir)
    else:
        logger.error("Conversion failed!")


def _perform_conversion(excel_file: str, input_dir: str, converted_dir: str) -> bool:
    """Perform the CSV conversion."""
    csv_file = _generate_output_filename(excel_file)
    logger.info("Converting %s to %s...", excel_file, csv_file)
    success = convert_excel_to_csv(get_file_path(excel_file, input_dir), get_file_path(csv_file, converted_dir))
    _log_conversion_result(success, converted_dir)
    return success


def _validate_and_select(input_dir: str, use_latest_file: bool) -> str:
    """Validate Excel files exist and select one."""
    excel_files = get_excel_files(input_dir)
    if not excel_files:
        logger.error("No Excel files found in %s", input_dir)
        return None
    
    excel_file = _select_excel_file_source(excel_files, input_dir, use_latest_file)
    if not excel_file:
        logger.error("No Excel file selected!")
    return excel_file


def _try_convert_excel(input_dir: str, converted_dir: str, use_latest_file: bool) -> bool:
    """Try to convert Excel with error handling."""
    excel_file = _validate_and_select(input_dir, use_latest_file)
    return _perform_conversion(excel_file, input_dir, converted_dir) if excel_file else False


def step_2_convert_excel_to_csv(use_latest_file: bool = None):
    """Step 2: Convert Excel to CSV."""
    input_dir = os.path.join("data", "input")
    converted_dir = os.path.join("data", "output", "converted", "csv")
    ensure_directory_exists(converted_dir)
    
    try:
        return _try_convert_excel(input_dir, converted_dir, use_latest_file)
    except (ValueError, Exception) as e:
        logger.exception("Error during conversion: %s", e)
        return False



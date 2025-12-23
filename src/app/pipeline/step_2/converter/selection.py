"""File selection logic."""

from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import get_excel_files
from src.app.pipeline.utils.file_selector import select_excel_file

logger = get_logger(__name__)

def get_excel_file_from_streamlit(excel_files: list) -> str:
    """Try to get Excel file from Streamlit session state."""
    try:
        import streamlit as st
        if hasattr(st, 'session_state') and 'selected_file' in st.session_state:
            excel_file = st.session_state['selected_file']
            logger.info("Using Streamlit selected file: %s", excel_file)
            return excel_file if excel_file in excel_files else None
    except (ImportError, RuntimeError):
        pass
    return None


def select_excel_file_source(excel_files: list, input_dir: str, use_latest_file: bool):
    """Select Excel file from Streamlit or selector."""
    excel_file = get_excel_file_from_streamlit(excel_files)
    if not excel_file:
        excel_file = select_excel_file(input_dir, excel_files, use_latest_file)
    return excel_file


def validate_and_select(input_dir: str, use_latest_file: bool) -> str:
    """Validate Excel files exist and select one."""
    excel_files = get_excel_files(input_dir)
    if not excel_files:
        logger.error("No Excel files found in %s", input_dir)
        return None
    
    excel_file = select_excel_file_source(excel_files, input_dir, use_latest_file)
    if not excel_file:
        logger.error("No Excel file selected!")
    return excel_file

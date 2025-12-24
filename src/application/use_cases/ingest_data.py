"""Use case for ingesting raw source data into the system."""

import os
from src.shared.utility.logging_utils import get_logger
from src.shared.utility.file_handler import ensure_directory_exists
from src.infrastructure.converters.converters.excel_to_csv import convert_excel_to_csv
from src.infrastructure.adapters.file_selector import FileSelectorService
from src.shared.config.paths import CONVERTED_DIR, INPUT_CSV_DIR

logger = get_logger(__name__)


class IngestData:
    """Orchestrates the conversion of raw Excel input to internal CSV format."""

    def __init__(self):
        self._input_directory = os.path.join("data", "input")
        self._output_directory = INPUT_CSV_DIR

    def execute(self, use_latest_file: bool = True, **kwargs) -> bool:
        """Selects an input Excel file and converts it to CSV."""
        ensure_directory_exists(self._output_directory)
        
        excel_filename = self._select_input_file(use_latest_file, **kwargs)
        if not excel_filename:
            logger.error("No Excel file found for ingestion.")
            return False

        input_path = os.path.join(self._input_directory, excel_filename)
        output_path = self._get_output_path(excel_filename)

        logger.info("Ingesting %s -> %s", excel_filename, output_path)
        success = convert_excel_to_csv(input_path, output_path)
        
        self._log_result(success, excel_filename, output_path)
        return success

    def _select_input_file(self, use_latest: bool, **kwargs) -> str:
        """Selects the appropriate Excel file based on priority."""
        filename = kwargs.get('filename')
        if filename:
            return filename
            
        filename = self._get_streamlit_selection()
        if filename:
            return filename
            
        return FileSelectorService.select_excel_file(
            self._input_directory, use_latest=use_latest
        )

    def _get_streamlit_selection(self) -> str:
        """Attempts to retrieve the selected file from Streamlit session state."""
        try:
            import streamlit as streamlit_lib
            state = streamlit_lib.session_state
            if (
                hasattr(streamlit_lib, 'session_state')
                and 'selected_file' in state
            ):
                logger.info(
                    "Using file from session state: %s", state['selected_file']
                )
                return state['selected_file']
        except (ImportError, RuntimeError):
            pass
        return None

    def _get_output_path(self, excel_filename: str) -> str:
        """Generates the target CSV output path."""
        base_name = os.path.splitext(excel_filename)[0]
        return os.path.join(self._output_directory, f"{base_name}.csv")

    def _log_result(self, success: bool, input_name: str, output_path: str) -> None:
        """Logs the final outcome of the ingestion process."""
        if success:
            logger.info("✓ Data ingestion completed: %s", output_path)
        else:
            logger.error("Data ingestion failed for: %s", input_name)

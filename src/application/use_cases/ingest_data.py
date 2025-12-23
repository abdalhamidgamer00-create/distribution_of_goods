"""Use case for ingesting raw source data into the system."""

import os
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import ensure_directory_exists
from src.services.conversion.converters.excel_to_csv import convert_excel_to_csv
from src.infrastructure.services.file_selector import FileSelectorService

logger = get_logger(__name__)

class IngestData:
    """Orchestrates the conversion of raw Excel input to internal CSV format."""

    def __init__(self):
        self._input_directory = os.path.join("data", "input")
        self._output_directory = os.path.join("data", "output", "converted", "csv")

    def execute(self, use_latest_file: bool = True, **kwargs) -> bool:
        """
        Selects an input Excel file and converts it to CSV.
        
        Args:
            use_latest_file: If True, automatically selects the newest file.
            **kwargs: Additional arguments (e.g., specific filename).
        """
        ensure_directory_exists(self._output_directory)

        # 1. Selection logic: prioritize provided filename, then Streamlit state, then latest.
        excel_filename = kwargs.get('filename')
        
        if not excel_filename:
            # Check Streamlit session state if available
            try:
                import streamlit as st
                if hasattr(st, 'session_state') and 'selected_file' in st.session_state:
                    excel_filename = st.session_state['selected_file']
                    logger.info("Using file from Streamlit session state: %s", excel_filename)
            except (ImportError, RuntimeError):
                pass
        
        if not excel_filename:
            excel_filename = FileSelectorService.select_excel_file(self._input_directory, use_latest=use_latest_file)

        if not excel_filename:
            logger.error("No Excel file found for ingestion in %s", self._input_directory)
            return False

        # 2. Define paths
        input_path = os.path.join(self._input_directory, excel_filename)
        
        # Consistent naming for output: same as input but .csv
        base_name = os.path.splitext(excel_filename)[0]
        csv_filename = f"{base_name}.csv"
        output_path = os.path.join(self._output_directory, csv_filename)

        # 3. Perform conversion
        logger.info("Ingesting %s -> %s", excel_filename, csv_filename)
        success = convert_excel_to_csv(input_path, output_path)

        if success:
            logger.info("✓ Data ingestion completed: %s", output_path)
        else:
            logger.error("Data ingestion failed for: %s", excel_filename)
            
        return success

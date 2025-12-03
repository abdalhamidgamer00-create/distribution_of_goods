"""Step 2: Convert Excel to CSV handler"""

import os
import re
from datetime import datetime
from src.services.conversion.converters.excel_to_csv import convert_excel_to_csv
from src.shared.utils.file_handler import ensure_directory_exists, get_file_path, get_excel_files
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.utils.file_selector import select_excel_file

logger = get_logger(__name__)


def step_2_convert_excel_to_csv(use_latest_file: bool = None):
    """Step 2: Convert Excel to CSV"""
    input_dir = os.path.join("data", "input")
    output_dir = os.path.join("data", "output")
    converted_dir = os.path.join("data", "output", "converted", "csv")
    
    ensure_directory_exists(converted_dir)
    
    excel_files = get_excel_files(input_dir)
    
    if not excel_files:
        logger.error("No Excel files found in %s", input_dir)
        return False
    
    try:
        # Check if running from Streamlit with selected file
        excel_file = None
        try:
            import streamlit as st
            if hasattr(st, 'session_state') and 'selected_file' in st.session_state:
                excel_file = st.session_state['selected_file']
                logger.info("Using Streamlit selected file: %s", excel_file)
                
                # Verify file exists
                if excel_file not in excel_files:
                    logger.error("Selected file not found in input directory: %s", excel_file)
                    return False
            else:
                # No file selected in session state, use normal selection
                excel_file = select_excel_file(input_dir, excel_files, use_latest_file)
        except (ImportError, RuntimeError):
            # Not in Streamlit context, use normal selection
            excel_file = select_excel_file(input_dir, excel_files, use_latest_file)
        
        if not excel_file:
            logger.error("No Excel file selected!")
            return False
        
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(excel_file)[0]
        base_name_clean = re.sub(r'_\d{8}_\d{6}', '', base_name)
        csv_file = f"{base_name_clean}_{date_str}.csv"
        
        input_path = get_file_path(excel_file, input_dir)
        output_path = get_file_path(csv_file, converted_dir)
        
        logger.info("Converting %s to %s...", excel_file, csv_file)
        success = convert_excel_to_csv(input_path, output_path)
        
        if success:
            logger.info("Conversion successful! File saved to: %s", converted_dir)
        else:
            logger.error("Conversion failed!")
        
        return success
        
    except ValueError as e:
        logger.error("Error: %s", e)
        return False
    except Exception as e:
        logger.exception("Error during conversion: %s", e)
        return False


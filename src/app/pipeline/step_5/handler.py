"""Step 5: Rename CSV columns handler"""

import os
import re
from datetime import datetime
from src.shared.utils.file_handler import get_file_path, get_csv_files, ensure_directory_exists
from src.services.conversion.converters.csv_column_renamer import rename_csv_columns
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.utils.file_selector import select_csv_file

logger = get_logger(__name__)


def _generate_renamed_filename(csv_file: str) -> str:
    """Generate output filename for renamed CSV."""
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(csv_file)[0]
    base_name_only = os.path.basename(base_name)
    base_name_clean = re.sub(r'_\d{8}_\d{6}', '', base_name_only)
    return f"{base_name_clean}_renamed_{date_str}.csv"


def step_5_rename_columns(use_latest_file: bool = None) -> bool:
    """Step 5: Rename CSV columns from Arabic to English."""
    output_dir = os.path.join("data", "output", "converted", "csv")
    renamed_dir = os.path.join("data", "output", "converted", "renamed")
    
    ensure_directory_exists(renamed_dir)
    
    csv_files = get_csv_files(output_dir)
    if not csv_files:
        logger.error("No CSV files found in %s", output_dir)
        return False
    
    try:
        csv_file = select_csv_file(output_dir, csv_files, use_latest_file)
        csv_path = get_file_path(csv_file, output_dir)
        
        output_file = _generate_renamed_filename(csv_file)
        output_path = get_file_path(output_file, renamed_dir)
        
        logger.info("Renaming columns in %s...", csv_file)
        logger.info("-" * 50)
        
        rename_csv_columns(csv_path, output_path)
        
        logger.info("Columns renamed successfully!")
        logger.info("Output file: %s", output_file)
        logger.info("Saved to: %s", renamed_dir)
        
        return True
        
    except ValueError as e:
        logger.error("Error: %s", e)
        return False
    except Exception as e:
        logger.exception("Error during column renaming: %s", e)
        return False



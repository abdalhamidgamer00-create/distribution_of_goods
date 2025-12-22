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


def _get_input_files(output_dir: str) -> list:
    """Get input CSV files and validate."""
    csv_files = get_csv_files(output_dir)
    if not csv_files:
        logger.error("No CSV files found in %s", output_dir)
        return None
    return csv_files


def _execute_rename(csv_path: str, csv_file: str, renamed_dir: str) -> bool:
    """Execute the rename operation."""
    output_file = _generate_renamed_filename(csv_file)
    output_path = get_file_path(output_file, renamed_dir)
    logger.info("Renaming columns in %s...\n" + "-" * 50, csv_file)
    rename_csv_columns(csv_path, output_path)
    logger.info("Columns renamed successfully!\nOutput file: %s\nSaved to: %s", output_file, renamed_dir)
    return True


def _process_rename(output_dir: str, csv_files: list, renamed_dir: str, use_latest_file: bool) -> bool:
    """Process the rename operation with error handling."""
    try:
        csv_file = select_csv_file(output_dir, csv_files, use_latest_file)
        return _execute_rename(get_file_path(csv_file, output_dir), csv_file, renamed_dir)
    except ValueError as e:
        logger.error("Error: %s", e)
        return False
    except Exception as e:
        logger.exception("Error during column renaming: %s", e); return False


def step_5_rename_columns(use_latest_file: bool = None) -> bool:
    """Step 5: Rename CSV columns from Arabic to English."""
    output_dir = os.path.join("data", "output", "converted", "csv")
    renamed_dir = os.path.join("data", "output", "converted", "renamed")
    ensure_directory_exists(renamed_dir)
    
    csv_files = _get_input_files(output_dir)
    if csv_files is None:
        return False
    
    return _process_rename(output_dir, csv_files, renamed_dir, use_latest_file)



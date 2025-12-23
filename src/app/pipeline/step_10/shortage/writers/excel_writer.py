"""Excel conversion logic for shortage files."""

import os
import pandas as pd
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def convert_all_to_excel(generated_files: dict, output_dir: str) -> None:
    """Convert all generated CSV files to Excel."""
    logger.info("Converting to Excel format...")
    for category, file_info in generated_files.items():
        base_name = os.path.basename(file_info['csv_path'])
        excel_filename = os.path.splitext(base_name)[0] + '.xlsx'
        excel_path = os.path.join(output_dir, excel_filename)
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                file_info['df'].to_excel(
                    writer, index=False, sheet_name='Shortage Products'
                )
        except Exception as error:
            logger.error(
                "Error creating Excel file for %s: %s", category, error
            )

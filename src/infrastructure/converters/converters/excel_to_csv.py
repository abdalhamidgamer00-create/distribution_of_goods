"""Convert Excel files to CSV"""

import pandas as pd
from pathlib import Path
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)


def _do_excel_conversion(input_path: str, output_path: str) -> None:
    """Perform the actual Excel to CSV conversion."""
    df = pd.read_excel(input_path)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')


def convert_excel_to_csv(input_path: str, output_path: str) -> bool:
    """Convert Excel file to CSV."""
    try:
        _do_excel_conversion(input_path, output_path)
        return True
    except Exception as e:
        logger.exception("Conversion error: %s", e)
        return False


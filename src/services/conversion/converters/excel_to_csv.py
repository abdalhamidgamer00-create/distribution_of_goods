"""Convert Excel files to CSV"""

import pandas as pd
from pathlib import Path
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def convert_excel_to_csv(input_path: str, output_path: str) -> bool:
    """
    Convert Excel file to CSV
    
    Args:
        input_path: Input Excel file path
        output_path: Output CSV file path
        
    Returns:
        True if conversion succeeded, False if failed
    """
    try:
        df = pd.read_excel(input_path)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        return True
    except Exception as e:
        logger.exception("Conversion error: %s", e)
        return False


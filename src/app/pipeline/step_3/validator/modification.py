"""File modification helpers."""

import pandas as pd
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def remove_first_row(csv_path: str, csv_file: str) -> bool:
    """Remove first row (header with date range) from CSV file."""
    logger.info(
        "Removing first row (header with date range) from %s...", csv_file
    )
    try:
        dataframe = pd.read_csv(
            csv_path, skiprows=1, encoding='utf-8-sig'
        )
        dataframe.to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info("✓ First row removed successfully")
        return True
    except Exception as error:
        logger.exception("✗ Error removing first row: %s", error)
        return False

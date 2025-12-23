"""Validation logic for shortage calculation."""

import pandas as pd
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

REQUIRED_COLUMNS = [
    'code', 'product_name', 'surplus_quantity', 
    'needed_quantity', 'balance', 'sales'
]


def has_required_columns(dataframe: pd.DataFrame, analytics_path: str) -> bool:
    """Check if DataFrame has all required columns."""
    missing_columns = [
        column for column in REQUIRED_COLUMNS 
        if column not in dataframe.columns
    ]
    if missing_columns:
        logger.warning(
            "Missing columns in %s: %s", analytics_path, missing_columns
        )
        return False
    return True

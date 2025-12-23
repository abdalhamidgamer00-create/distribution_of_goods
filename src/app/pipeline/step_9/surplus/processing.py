"""Surplus calculation logic."""

from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_9.surplus_calculator import (
    calculate_total_withdrawals,
    calculate_remaining_surplus,
)
from src.app.pipeline.step_9.file_generator import add_product_type_column

logger = get_logger(__name__)


def calculate_branch_surplus(dataframe, branch: str, analytics_dir: str):
    """Calculate remaining surplus for a branch."""
    total_withdrawals = calculate_total_withdrawals(analytics_dir, branch)
    result_dataframe = calculate_remaining_surplus(dataframe, total_withdrawals)
    
    if result_dataframe.empty:
        logger.info("No remaining surplus for branch: %s", branch)
        return None
    
    return add_product_type_column(result_dataframe)

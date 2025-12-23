"""Data loading and preparation for shortage generation."""

import os
from src.shared.utils.logging_utils import get_logger
from src.core.domain.classification.product_classifier import (
    classify_product_type,
)
from src.app.pipeline.step_10.shortage_calculator import (
    calculate_shortage_products,
)

logger = get_logger(__name__)


def validate_analytics_directories(branches: list, base_dir: str) -> bool:
    """Validate that analytics directories exist for all branches."""
    for branch in branches:
        branch_dir = os.path.join(base_dir, branch)
        if not os.path.exists(branch_dir):
            logger.error("Analytics directory not found: %s", branch_dir)
            logger.error("Please run step 6 (Split by Branches) first")
            return False
    return True


def prepare_shortage_data(analytics_dir: str) -> tuple:
    """Prepare shortage data and classify products."""
    result = calculate_shortage_products(analytics_dir)
    shortage_dataframe, has_date_header, first_line = result
    
    if shortage_dataframe.empty:
        return None, None, None
    
    shortage_dataframe['product_type'] = (
        shortage_dataframe['product_name'].apply(classify_product_type)
    )
    return shortage_dataframe, has_date_header, first_line

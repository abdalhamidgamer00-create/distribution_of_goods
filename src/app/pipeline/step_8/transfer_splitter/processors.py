"""File splitting logic for Step 8."""

from src.shared.utils.logging_utils import get_logger
from src.core.domain.classification.product_classifier import (
    get_product_categories,
)
from src.services.transfers.splitters.file_splitter import (
    split_all_transfer_files,
)

logger = get_logger(__name__)


def execute_split_and_log(
    transfers_base_dir: str, 
    has_date_header: bool, 
    first_line: str
) -> bool:
    """Execute splitting and log results."""
    all_output_files = split_all_transfer_files(
        transfers_base_dir, has_date_header, first_line
    )
    if not all_output_files:
        logger.warning("No files were split")
        return False
    categories = get_product_categories()
    log_split_summary(all_output_files, categories)
    logger.info("Split files saved to: %s", transfers_base_dir)
    return True


def log_split_summary(all_output_files: dict, categories: list) -> None:
    """Log summary of split files."""
    category_counts = {category: 0 for category in categories}
    for (_, _, category), _ in all_output_files.items():
        category_counts[category] = category_counts.get(category, 0) + 1
    
    logger.info("Generated %s split files:", len(all_output_files))
    for category in categories:
        count = category_counts[category]
        if count > 0:
            logger.info("  - %s: %s files", category, count)

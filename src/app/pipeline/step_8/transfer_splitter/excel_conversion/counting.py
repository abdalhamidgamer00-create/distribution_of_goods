"""Excel counting and logging logic."""

import os
from src.shared.utils.logging_utils import get_logger
from src.core.domain.classification.product_classifier import get_product_categories

logger = get_logger(__name__)


def count_single_excel_file(
    file: str, 
    categories: list, 
    category_counts: dict
) -> None:
    """Count a single Excel file's category."""
    if file.endswith('.xlsx'):
        for category in categories:
            if file.endswith(f'_{category}.xlsx'):
                category_counts[category] += 1
                break


def count_excel_by_category(excel_output_dir: str) -> dict:
    """Count Excel files by category."""
    categories = get_product_categories()
    category_counts = {category: 0 for category in categories}
    if not os.path.exists(excel_output_dir):
        return category_counts
    for _, _, files in os.walk(excel_output_dir):
        for file in files:
            count_single_excel_file(file, categories, category_counts)
    return category_counts


def log_excel_summary(excel_count: int, excel_output_dir: str) -> None:
    """Log summary of generated Excel files."""
    categories = get_product_categories()
    category_counts = count_excel_by_category(excel_output_dir)
    
    logger.info("Generated %s Excel files:", excel_count)
    for category in categories:
        count = category_counts[category]
        if count > 0:
            logger.info("  - %s: %s files", category, count)
    logger.info("Excel files saved to: %s", excel_output_dir)

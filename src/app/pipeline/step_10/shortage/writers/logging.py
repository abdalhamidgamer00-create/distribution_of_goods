"""Logging logic for shortage generation summary."""

from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def log_summary(
    generated_files: dict, 
    categories: list, 
    total_shortage: int,
    csv_output_dir: str,
    excel_output_dir: str
) -> None:
    """Log generation summary."""
    logger.info("=" * 50 + "\nGenerated shortage files:")
    for category in categories:
        if category in generated_files:
            logger.info(
                "  - %s: %d products", category, generated_files[category]['count']
            )
            
    logger.info(
        "  - all (combined): %d products\n\n"
        "Total shortage quantity: %d units\n\n"
        "CSV files saved to: %s\nExcel files saved to: %s", 
        generated_files['all']['count'], 
        total_shortage, 
        csv_output_dir, 
        excel_output_dir
    )

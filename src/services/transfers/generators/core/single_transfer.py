"""Single transfer processing logic."""

from src.services.transfers.generators.core import loading, builder, writer
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

def process_transfer(
    analytics_path: str, 
    source_branch: str, 
    target_branch: str, 
    transfers_dir: str, 
    base_name: str, 
    has_date_header: bool, 
    first_line: str
) -> str:
    """Process transfer from analytics file."""
    analytics_dataframe = loading.load_analytics_file(analytics_path)
    transfer_dataframe = builder.build_and_validate_transfer(
        analytics_dataframe, source_branch, target_branch
    )
    
    if transfer_dataframe is None:
        return None
    
    return writer.save_transfer_file(
        transfer_dataframe, 
        transfers_dir, 
        source_branch, 
        target_branch, 
        base_name, 
        has_date_header, 
        first_line
    )


def execute_transfer_process(
    analytics_path: str, 
    source_branch: str, 
    target_branch: str,
    transfers_dir: str, 
    base_name: str, 
    has_date_header: bool, 
    first_line: str
) -> str:
    """Execute transfer process with error handling."""
    try:
        return process_transfer(
            analytics_path, 
            source_branch, 
            target_branch, 
            transfers_dir, 
            base_name, 
            has_date_header, 
            first_line
        )
    except (ValueError, FileNotFoundError):
        return None
    except Exception as error:
        logger.exception(
            "Warning: Error processing %s -> %s: %s", 
            source_branch, 
            target_branch, 
            error
        )
        return None

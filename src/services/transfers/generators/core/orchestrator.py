"""Orchestrator for transfer generation."""

from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.services.transfers.generators.core import (
    loading,
    builder,
    writer,
)

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


def generate_transfer_for_pair(
    source_branch: str, 
    target_branch: str, 
    analytics_dir: str,
    transfers_dir: str, 
    has_date_header: bool = False, 
    first_line: str = ""
) -> str:
    """Generate transfer CSV file from source branch to target branch."""
    analytics_path, _, base_name = loading.get_analytics_path(
        analytics_dir, target_branch
    )
    
    if not analytics_path:
        return None
    
    return execute_transfer_process(
        analytics_path, 
        source_branch, 
        target_branch,
        transfers_dir, 
        base_name, 
        has_date_header, 
        first_line
    )


def collect_transfer_pairs(branches: list) -> list:
    """Collect all valid source-target pairs."""
    return [
        (source, target) 
        for source in branches 
        for target in branches 
        if source != target
    ]


def generate_for_all_pairs(
    branches: list, 
    analytics_dir: str, 
    transfers_dir: str,
    has_date_header: bool, 
    first_line: str
) -> dict:
    """Generate transfers for all branch pairs."""
    transfer_files = {}
    for source_branch, target_branch in collect_transfer_pairs(branches):
        transfer_path = generate_transfer_for_pair(
            source_branch, 
            target_branch, 
            analytics_dir, 
            transfers_dir, 
            has_date_header, 
            first_line
        )
        if transfer_path:
            transfer_files[(source_branch, target_branch)] = transfer_path
    return transfer_files


def generate_transfer_files(
    analytics_dir: str, 
    transfers_dir: str, 
    has_date_header: bool = False, 
    first_line: str = ""
) -> dict:
    """Generate transfer CSV files for each source branch to all 
    target branches."""
    return generate_for_all_pairs(
        get_branches(), 
        analytics_dir, 
        transfers_dir, 
        has_date_header, 
        first_line
    )

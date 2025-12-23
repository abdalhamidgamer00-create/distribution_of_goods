"""Batch transfer processing logic."""

from src.core.domain.branches.config import get_branches
from src.services.transfers.generators.core import loading
from src.services.transfers.generators.core.single_transfer import execute_transfer_process


def collect_transfer_pairs(branches: list) -> list:
    """Collect all valid source-target pairs."""
    return [
        (source, target) 
        for source in branches 
        for target in branches 
        if source != target
    ]


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

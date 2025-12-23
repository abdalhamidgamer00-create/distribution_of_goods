"""Orchestrator for transfer generation facade."""

from src.core.domain.branches.config import get_branches
from src.services.transfers.generators.core.batch_processing import (
    generate_for_all_pairs,
    generate_transfer_for_pair
)

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

__all__ = ['generate_transfer_files', 'generate_transfer_for_pair']

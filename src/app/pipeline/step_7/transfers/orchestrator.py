"""Orchestrator for Step 7 transfer generation."""

import os
from src.core.domain.branches.config import get_branches
from src.app.pipeline.step_7.transfers import finders, generators


def step_7_generate_transfers(use_latest_file: bool = None) -> bool:
    """Step 7: Generate transfer CSV files between branches."""
    analytics_dir = os.path.join("data", "output", "branches", "analytics")
    transfers_base_dir = os.path.join("data", "output", "transfers", "csv")
    
    analytics_files = finders.validate_and_get_files(
        analytics_dir, get_branches()
    )
    if analytics_files is None:
        return False
    
    return generators.run_transfer_generation(
        analytics_dir, transfers_base_dir, analytics_files
    )

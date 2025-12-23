"""Step 8: Split transfer files by product type handler.

This module is a facade for the transfer splitting orchestration.
"""

from src.app.pipeline.step_8.transfer_splitter.orchestrator import (
    run_split_by_product_type,
)


def step_8_split_by_product_type(use_latest_file: bool = None) -> bool:
    """Step 8: Split transfer files by product type."""
    return run_split_by_product_type()

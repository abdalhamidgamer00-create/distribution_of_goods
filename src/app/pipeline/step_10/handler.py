"""Step 10: Generate shortage files handler.

This module is a facade for the shortage generation orchestration.
"""

from src.app.pipeline.step_10.shortage.orchestrator import (
    run_shortage_generation
)


def step_10_generate_shortage_files(use_latest_file: bool = None) -> bool:
    """Step 10: Generate shortage files."""
    return run_shortage_generation()

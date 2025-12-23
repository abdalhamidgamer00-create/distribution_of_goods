"""Step 9: Generate remaining surplus files handler.

This module is a facade for the surplus generation orchestration.
"""

from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_9.surplus.orchestrator import run_surplus_generation

logger = get_logger(__name__)


def step_9_generate_remaining_surplus(use_latest_file: bool = None) -> bool:
    """Step 9: Generate remaining surplus files for each branch."""
    try:
        return run_surplus_generation()
    except Exception as error:
        logger.exception("Error generating remaining surplus files: %s", error)
        return False

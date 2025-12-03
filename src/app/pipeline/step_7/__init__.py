"""Step 7: Generate Transfer Files

Generates transfer CSV files for each branch to all other branches.
"""

from src.app.pipeline.step_7.handler import step_7_generate_transfers

__all__ = ['step_7_generate_transfers']


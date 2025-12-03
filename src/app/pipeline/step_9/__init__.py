"""Step 9: Generate Remaining Surplus Files

This module handles generating files for products with remaining surplus
after distribution to all needing branches.

Submodules:
- analytics_reader: Reads analytics files and extracts withdrawal data
- surplus_calculator: Calculates remaining surplus for each branch
- file_generator: Generates CSV and Excel output files
"""

from src.app.pipeline.step_9.handler import step_9_generate_remaining_surplus

__all__ = ['step_9_generate_remaining_surplus']


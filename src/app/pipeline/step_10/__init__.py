"""Step 10: Generate Shortage Files

Generates files for products with shortage (needed quantity exceeds total surplus).
These are products that branches need but no other branch has surplus to cover.
"""

from src.app.pipeline.step_10.handler import step_10_generate_shortage_files

__all__ = ['step_10_generate_shortage_files']


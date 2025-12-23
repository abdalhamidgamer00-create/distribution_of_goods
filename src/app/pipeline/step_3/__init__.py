"""Step 3: Validate Data

Validates CSV data, checks date range (>= 3 months) and column headers.
"""

from src.app.pipeline.step_3.validator import step_3_validate_data

__all__ = ['step_3_validate_data']


"""Step 8: Split Transfer Files by Product Type

Splits transfer files into 6 categories: tablets_and_capsules, injections,
syrups, creams, sachets, other.
"""

from src.app.pipeline.step_8.handler import step_8_split_by_product_type

__all__ = ['step_8_split_by_product_type']


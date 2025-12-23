"""Utility helper functions."""

import os
from datetime import datetime


def get_timestamp() -> str:
    """Get current timestamp string for file naming."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def extract_base_name(filename: str, branch: str) -> str:
    """Extract base name from analytics filename without branch suffix."""
    base = os.path.splitext(filename)[0]
    return base.replace(f'_{branch}_analytics', '')

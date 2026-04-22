"""Text and scalar helpers for transfer ratio services."""

from __future__ import annotations

import os
import re

import pandas as pd


def normalize_header(value: object) -> str:
    """Normalize headers and tokens into a stable representation."""
    text = clean_text(value).lower()
    text = text.replace("-", "_").replace("/", "_").replace("\\", "_")
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def clean_text(value: object) -> str:
    """Convert arbitrary values into clean strings."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def extract_name(file_obj) -> str:
    """Extract a display name from a path or uploaded file object."""
    if isinstance(file_obj, str):
        return os.path.basename(file_obj)
    return getattr(file_obj, "name", "uploaded_file.xlsx")


def to_percentage(numerator: float, denominator: float) -> float:
    """Safely convert a ratio into a percentage."""
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)

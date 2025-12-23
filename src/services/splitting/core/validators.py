"""Validation helpers for splitter."""
import os
from src.core.domain.branches.config import get_branches

def validate_csv_input(csv_path: str) -> None:
    """Validate CSV file exists and is not empty."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    if os.path.getsize(csv_path) == 0:
        raise ValueError(f"CSV file is empty: {csv_path}")


def validate_branch_data(branch_data: dict, timing_stats: dict) -> int:
    """Validate branch data and return num_products."""
    if not branch_data or get_branches()[0] not in branch_data:
        raise ValueError("No data found in CSV file")
    
    num_products = len(branch_data[get_branches()[0]])
    if num_products == 0:
        raise ValueError("CSV file contains no products")
    timing_stats["num_products"] = num_products
    return num_products

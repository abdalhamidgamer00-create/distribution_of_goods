"""Data preparation logic."""

from time import perf_counter
from src.services.splitting.processors.data_preparer import prepare_branch_data
from src.core.domain.calculations.allocation_calculator import calculate_proportional_allocations_vectorized
from src.services.splitting.core.validators import validate_branch_data

def prepare_branch_data_with_timing(csv_path: str, timing_stats: dict) -> tuple:
    """Prepare branch data and track timing."""
    prep_start = perf_counter()
    branch_data, has_date_header, first_line = prepare_branch_data(csv_path)
    timing_stats["prep_time"] = perf_counter() - prep_start
    
    num_products = validate_branch_data(branch_data, timing_stats)
    return branch_data, has_date_header, first_line, num_products


def calculate_allocations(branch_data: dict, branches: list, timing_stats: dict) -> dict:
    """Calculate proportional allocations with timing."""
    allocation_start = perf_counter()
    proportional_allocation = calculate_proportional_allocations_vectorized(branch_data, branches)
    timing_stats["allocation_time"] = perf_counter() - allocation_start
    return proportional_allocation

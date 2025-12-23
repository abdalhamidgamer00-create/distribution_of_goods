"""Main splitter orchestration."""
import os
from time import perf_counter
from src.core.domain.branches.config import get_branches
from src.services.splitting.processors.data_preparer import prepare_branch_data
from src.core.domain.calculations.allocation_calculator import calculate_proportional_allocations_vectorized
from src.core.domain.calculations.quantity_calculator import calculate_surplus_remaining
from src.services.splitting.processors.withdrawal_processor import process_withdrawals
from src.services.splitting.writers.file_writer import write_branch_files, write_analytics_files
from src.services.splitting.surplus import redistribute_wasted_surplus
from src.shared.utils.logging_utils import get_logger

from .validators import validate_csv_input, validate_branch_data
from .analytics import initialize_analytics_data, fill_empty_product_records
from .distributor import process_all_products

logger = get_logger(__name__)

def split_csv_by_branches(csv_path: str, output_base_dir: str, base_filename: str, analytics_dir: str = None) -> tuple:
    """Split CSV file by branches into separate files."""
    validate_csv_input(csv_path)
    branches, timing_stats = get_branches(), {}
    try:
        return _execute_split(csv_path, output_base_dir, base_filename, analytics_dir, branches, timing_stats)
    except (FileNotFoundError, ValueError):
        raise
    except Exception as error:
        logger.exception("Error splitting CSV: %s", error)
        raise ValueError(f"Error splitting CSV: {error}") from error


def _execute_split(csv_path: str, output_base_dir: str, base_filename: str, 
                   analytics_dir: str, branches: list, timing_stats: dict) -> tuple:
    """Execute the splitting process."""
    branch_data, has_date_header, first_line, num_products = _prepare_branch_data_with_timing(csv_path, timing_stats)
    proportional_allocation = _calculate_allocations(branch_data, branches, timing_stats)
    
    processed_data, max_withdrawals = _run_processing_pipeline(
        branches, branch_data, proportional_allocation, num_products, timing_stats
    )
    output_files = _write_output_files(
        branches, processed_data, output_base_dir, base_filename, analytics_dir, 
        max_withdrawals, has_date_header, first_line, timing_stats
    )
    
    return output_files, timing_stats


def _prepare_branch_data_with_timing(csv_path: str, timing_stats: dict) -> tuple:
    """Prepare branch data and track timing."""
    prep_start = perf_counter()
    branch_data, has_date_header, first_line = prepare_branch_data(csv_path)
    timing_stats["prep_time"] = perf_counter() - prep_start
    
    num_products = validate_branch_data(branch_data, timing_stats)
    return branch_data, has_date_header, first_line, num_products


def _calculate_allocations(branch_data: dict, branches: list, timing_stats: dict) -> dict:
    """Calculate proportional allocations with timing."""
    allocation_start = perf_counter()
    proportional_allocation = calculate_proportional_allocations_vectorized(branch_data, branches)
    timing_stats["allocation_time"] = perf_counter() - allocation_start
    return proportional_allocation


def _run_processing_pipeline(branches: list, branch_data: dict, proportional_allocation: dict, 
                              num_products: int, timing_stats: dict) -> tuple:
    """Run the processing pipeline and return processed data."""
    analytics_data, all_withdrawals, max_withdrawals = _process_surplus_distribution(
        branches, branch_data, proportional_allocation, num_products, timing_stats
    )
    final_surplus_remaining_dict = calculate_surplus_remaining(branches, branch_data, all_withdrawals)
    processed_data = process_withdrawals(branches, analytics_data, max_withdrawals, final_surplus_remaining_dict)
    return processed_data, max_withdrawals


def _process_surplus_distribution(branches: list, branch_data: dict, proportional_allocation: dict, 
                                  num_products: int, timing_stats: dict) -> tuple:
    """Process surplus distribution and redistribution."""
    surplus_start = perf_counter()
    analytics_data = initialize_analytics_data(branches, branch_data)
    all_withdrawals, max_withdrawals = process_all_products(
        branches, branch_data, analytics_data, proportional_allocation, num_products
    )
    fill_empty_product_records(branches, analytics_data, num_products)
    timing_stats["surplus_time"] = perf_counter() - surplus_start
    
    max_withdrawals, timing_stats["second_round_time"] = redistribute_wasted_surplus(
        branches, branch_data, analytics_data, all_withdrawals, max_withdrawals, num_products, 30.0
    )
    return analytics_data, all_withdrawals, max_withdrawals


def _write_output_files(branches: list, processed_data: dict, output_base_dir: str, base_filename: str,
                        analytics_dir: str, max_withdrawals: int, has_date_header: bool, 
                        first_line: str, timing_stats: dict) -> dict:
    """Write branch and analytics files."""
    write_start = perf_counter()
    output_files = write_branch_files(branches, processed_data, output_base_dir, base_filename, has_date_header, first_line)
    if analytics_dir is None:
        analytics_dir = os.path.normpath(os.path.join(output_base_dir, "..", "analytics"))
    write_analytics_files(branches, processed_data, analytics_dir, base_filename, max_withdrawals, has_date_header, first_line)
    timing_stats["write_time"] = perf_counter() - write_start
    return output_files

"""CSV branch splitter"""

import os
from time import perf_counter

from src.core.domain.branches.config import get_branches
from src.services.splitting.processors.data_preparer import prepare_branch_data
from src.core.domain.calculations.allocation_calculator import (
    calculate_proportional_allocations_vectorized,
)
from src.core.domain.calculations.order_calculator import get_needing_branches_order_for_product
from src.services.splitting.processors.surplus_finder import (
    find_surplus_sources_for_single_product,
)
from src.core.domain.calculations.quantity_calculator import calculate_surplus_remaining
from src.services.splitting.processors.withdrawal_processor import process_withdrawals
from src.services.splitting.writers.file_writer import write_branch_files, write_analytics_files
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _validate_csv_input(csv_path: str) -> None:
    """Validate CSV file exists and is not empty."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    if os.path.getsize(csv_path) == 0:
        raise ValueError(f"CSV file is empty: {csv_path}")


def _initialize_analytics_data(branches: list, branch_data: dict) -> dict:
    """Initialize analytics data structure for each branch."""
    analytics_data = {}
    for branch in branches:
        branch_df = branch_data[branch].copy()
        analytics_data[branch] = (branch_df, [])
    return analytics_data


def _create_empty_withdrawal_record() -> dict:
    """Create an empty withdrawal record."""
    return {
        'surplus_from_branch': 0.0,
        'available_branch': '',
        'surplus_remaining': 0.0,
        'remaining_needed': 0.0
    }


def _process_all_products(
    branches: list,
    branch_data: dict,
    analytics_data: dict,
    proportional_allocation: dict,
    num_products: int
) -> tuple:
    """Process all products and return withdrawals data."""
    all_withdrawals = {}
    max_withdrawals = 0
    
    for product_idx in range(num_products):
        needing_branches = get_needing_branches_order_for_product(product_idx, branch_data, branches)
        
        for branch in needing_branches:
            branch_df = analytics_data[branch][0]
            needed = branch_df.iloc[product_idx]['needed_quantity']
            
            if needed <= 0:
                continue
            
            withdrawals_list, withdrawals = find_surplus_sources_for_single_product(
                branch, product_idx, branch_data, branches, all_withdrawals, proportional_allocation
            )
            
            for key, amount in withdrawals.items():
                all_withdrawals[key] = all_withdrawals.get(key, 0.0) + amount
            
            existing_withdrawals_list = analytics_data[branch][1]
            while len(existing_withdrawals_list) < product_idx:
                existing_withdrawals_list.append([_create_empty_withdrawal_record()])
            existing_withdrawals_list.append(withdrawals_list)
            
            max_withdrawals = max(max_withdrawals, len(withdrawals_list))
    
    return all_withdrawals, max_withdrawals


def _fill_empty_product_records(branches: list, analytics_data: dict, num_products: int) -> None:
    """Add empty records for products that weren't processed."""
    for branch in branches:
        branch_df = analytics_data[branch][0]
        existing_list = analytics_data[branch][1]
        
        for product_idx in range(len(existing_list), num_products):
            if branch_df.iloc[product_idx]['needed_quantity'] <= 0:
                existing_list.append([_create_empty_withdrawal_record()])


def _prepare_branch_data_with_timing(csv_path: str, timing_stats: dict) -> tuple:
    """Prepare branch data and track timing."""
    prep_start = perf_counter()
    branch_data, has_date_header, first_line = prepare_branch_data(csv_path)
    timing_stats["prep_time"] = perf_counter() - prep_start
    
    if not branch_data or get_branches()[0] not in branch_data:
        raise ValueError("No data found in CSV file")
    
    num_products = len(branch_data[get_branches()[0]])
    timing_stats["num_products"] = num_products
    if num_products == 0:
        raise ValueError("CSV file contains no products")
    
    return branch_data, has_date_header, first_line, num_products


def _calculate_allocations(branch_data: dict, branches: list, timing_stats: dict) -> dict:
    """Calculate proportional allocations with timing."""
    allocation_start = perf_counter()
    proportional_allocation = calculate_proportional_allocations_vectorized(branch_data, branches)
    timing_stats["allocation_time"] = perf_counter() - allocation_start
    return proportional_allocation


def _process_surplus_distribution(branches: list, branch_data: dict, proportional_allocation: dict, 
                                  num_products: int, timing_stats: dict) -> tuple:
    """Process surplus distribution and redistribution."""
    surplus_start = perf_counter()
    analytics_data = _initialize_analytics_data(branches, branch_data)
    all_withdrawals, max_withdrawals = _process_all_products(
        branches, branch_data, analytics_data, proportional_allocation, num_products
    )
    _fill_empty_product_records(branches, analytics_data, num_products)
    timing_stats["surplus_time"] = perf_counter() - surplus_start
    
    from src.services.splitting.processors.surplus_redistributor import redistribute_wasted_surplus
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


def split_csv_by_branches(csv_path: str, output_base_dir: str, base_filename: str, analytics_dir: str = None) -> tuple:
    """Split CSV file by branches into separate files."""
    _validate_csv_input(csv_path)
    
    timing_stats = {}
    branches = get_branches()
    
    try:
        branch_data, has_date_header, first_line, num_products = _prepare_branch_data_with_timing(csv_path, timing_stats)
        proportional_allocation = _calculate_allocations(branch_data, branches, timing_stats)
        analytics_data, all_withdrawals, max_withdrawals = _process_surplus_distribution(
            branches, branch_data, proportional_allocation, num_products, timing_stats
        )
        
        final_surplus_remaining_dict = calculate_surplus_remaining(branches, branch_data, all_withdrawals)
        processed_data = process_withdrawals(branches, analytics_data, max_withdrawals, final_surplus_remaining_dict)
        
        output_files = _write_output_files(
            branches, processed_data, output_base_dir, base_filename, analytics_dir,
            max_withdrawals, has_date_header, first_line, timing_stats
        )
        
        return output_files, timing_stats
        
    except (FileNotFoundError, ValueError):
        raise
    except Exception as e:
        logger.exception("Error splitting CSV: %s", e)
        raise ValueError(f"Error splitting CSV: {e}") from e


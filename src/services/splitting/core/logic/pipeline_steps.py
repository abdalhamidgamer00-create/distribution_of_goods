"""Pipeline processing logic."""

from time import perf_counter
from src.core.domain.calculations.quantity_calculator import calculate_surplus_remaining
from src.services.splitting.processors.withdrawal_processor import process_withdrawals
from src.services.splitting.surplus import redistribute_wasted_surplus
from src.services.splitting.core.analytics import initialize_analytics_data, fill_empty_product_records
from src.services.splitting.core.distributor import process_all_products

def run_processing_pipeline(branches: list, branch_data: dict, proportional_allocation: dict, 
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

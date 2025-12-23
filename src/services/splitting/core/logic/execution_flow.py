"""Execution flow logic."""

from src.services.splitting.core.logic.preparation import prepare_branch_data_with_timing, calculate_allocations
from src.services.splitting.core.logic.pipeline_steps import run_processing_pipeline
from src.services.splitting.core.logic.output_handling import write_output_files

def execute_split(csv_path: str, output_base_dir: str, base_filename: str, 
                   analytics_dir: str, branches: list, timing_stats: dict) -> tuple:
    """Execute the splitting process."""
    branch_data, has_date_header, first_line, num_products = prepare_branch_data_with_timing(csv_path, timing_stats)
    proportional_allocation = calculate_allocations(branch_data, branches, timing_stats)
    
    processed_data, max_withdrawals = run_processing_pipeline(
        branches, branch_data, proportional_allocation, num_products, timing_stats
    )
    output_files = write_output_files(
        branches, processed_data, output_base_dir, base_filename, analytics_dir, 
        max_withdrawals, has_date_header, first_line, timing_stats
    )
    
    return output_files, timing_stats

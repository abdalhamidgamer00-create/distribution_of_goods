"""Main orchestrator for surplus generation step."""

import os
from src.shared.utils.logging_utils import get_logger
from src.core.domain.branches.config import get_branches
from src.app.pipeline.step_9.surplus import loading, processing, writers

logger = get_logger(__name__)

# Constants
ANALYTICS_DIR = os.path.join("data", "output", "branches", "analytics")
CSV_OUTPUT_DIR = os.path.join("data", "output", "remaining_surplus", "csv")
EXCEL_OUTPUT_DIR = os.path.join("data", "output", "remaining_surplus", "excel")


def _process_branch(branch: str) -> dict:
    """Process a single branch and generate its remaining surplus files."""
    loaded_data = loading.load_and_validate_analytics(branch, ANALYTICS_DIR)
    if not loaded_data or loaded_data[0] is None:
        return None
    
    dataframe, has_date_header, first_line = loaded_data
    
    result_dataframe = processing.calculate_branch_surplus(
        dataframe, branch, ANALYTICS_DIR
    )
    if result_dataframe is None:
        return None
    
    return writers.generate_branch_files(
        result_dataframe, 
        branch, 
        has_date_header, 
        first_line,
        ANALYTICS_DIR,
        CSV_OUTPUT_DIR
    )


def _process_all_branches(branches: list) -> dict:
    """Process all branches and collect generated files."""
    all_branch_files = {}
    
    for branch in branches:
        branch_files = _process_branch(branch)
        if branch_files:
            all_branch_files[branch] = branch_files
    
    return all_branch_files


def run_surplus_generation(branches: list = None) -> bool:
    """Execute the surplus file generation process."""
    if branches is None:
        branches = get_branches()

    if not loading.validate_analytics_directories(branches, ANALYTICS_DIR):
        return False

    all_branch_files = _process_all_branches(branches)
    
    if not all_branch_files:
        logger.warning("No remaining surplus files were created")
        return False
    
    writers.convert_all_to_excel(all_branch_files, EXCEL_OUTPUT_DIR)
    writers.log_summary(all_branch_files, CSV_OUTPUT_DIR, EXCEL_OUTPUT_DIR)
    return True

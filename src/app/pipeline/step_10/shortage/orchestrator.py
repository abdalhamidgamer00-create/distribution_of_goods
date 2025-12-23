"""Orchestrator for Step 10 shortage generation."""

import os
from src.shared.utils.logging_utils import get_logger
from src.core.domain.branches.config import get_branches
from src.app.pipeline.step_10.shortage import loading, writers

logger = get_logger(__name__)

# Constants
ANALYTICS_DIR = os.path.join("data", "output", "branches", "analytics")
CSV_OUTPUT_DIR = os.path.join("data", "output", "shortage", "csv")
EXCEL_OUTPUT_DIR = os.path.join("data", "output", "shortage", "excel")


def execute_shortage_generation(
    shortage_dataframe, 
    has_date_header: bool, 
    first_line: str
) -> bool:
    """Execute the shortage file generation process."""
    logger.info("Found %d products with shortage", len(shortage_dataframe))
    
    generated_files, categories = writers.generate_all_files(
        shortage_dataframe, 
        has_date_header, 
        first_line,
        CSV_OUTPUT_DIR,
        EXCEL_OUTPUT_DIR
    )
    
    writers.convert_all_to_excel(generated_files, EXCEL_OUTPUT_DIR)
    
    total_shortage = int(shortage_dataframe['shortage_quantity'].sum())
    writers.log_summary(
        generated_files, 
        categories, 
        total_shortage,
        CSV_OUTPUT_DIR,
        EXCEL_OUTPUT_DIR
    )
    
    return True


def run_shortage_generation() -> bool:
    """Run the shortage generation process."""
    if not loading.validate_analytics_directories(
        get_branches(), ANALYTICS_DIR
    ):
        return False

    try:
        logger.info("Calculating shortage products...\n" + "-" * 50)
        
        load_result = loading.prepare_shortage_data(ANALYTICS_DIR)
        
        if load_result[0] is None:
            # Check if it was purely empty or error? 
            # Original code: return None -> "No shortage products found"
            # But prepare_shortage_data returns None, None, None if empty
            
            # Need to distinguish between 'no analytics' (error) and 'no shortage' (success)
            # In loading.py, prepare_shortage_data calls calculate_shortage_products
            # calculate_shortage_products returns empty DF if no shortage.
            # loading.prepare_shortage_data returns None if empty.
            
            logger.info(
                "No shortage products found. All needs are covered by surplus!"
            )
            return True
        
        shortage_dataframe, has_date_header, first_line = load_result
        return execute_shortage_generation(
            shortage_dataframe, has_date_header, first_line
        )
        
    except Exception as error:
        logger.exception("Error generating shortage files: %s", error)
        return False

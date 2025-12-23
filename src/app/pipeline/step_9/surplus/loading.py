from src.app.pipeline.step_9.surplus_calculator import (
    validate_analytics_columns,
)

logger = get_logger(__name__)


def validate_analytics_directories(branches: list, base_dir: str) -> bool:
    """Check that all branch analytics directories exist."""
    for branch in branches:
        branch_dir = os.path.join(base_dir, branch)
        if not os.path.exists(branch_dir):
            logger.error("Analytics directory not found: %s", branch_dir)
            logger.error("Please run step 6 (Split by Branches) first")
            return False
    return True


def validate_columns(dataframe, analytics_path: str) -> bool:
    """Validate analytics columns and return success status."""
    missing_columns = validate_analytics_columns(dataframe)
    if missing_columns:
        logger.error(
            "Missing required columns in %s: %s", 
            analytics_path, 
            missing_columns
        )
        return False
    return True


def load_and_validate_analytics(branch: str, base_dir: str):
    """Load and validate analytics file for a branch."""
    analytics_path = get_latest_analytics_path(base_dir, branch)
    if not analytics_path:
        logger.warning("No analytics file found for branch: %s", branch)
        return None, None, None
        
    dataframe, has_date_header, first_line = read_analytics_file(analytics_path)
    if dataframe is None or not validate_columns(dataframe, analytics_path):
        return None, None, None
        
    return dataframe, has_date_header, first_line

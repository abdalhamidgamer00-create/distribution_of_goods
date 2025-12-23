"""Main splitter orchestration facade."""

from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.services.splitting.core.validators import validate_csv_input
from src.services.splitting.core.logic import execute_split

logger = get_logger(__name__)

def split_csv_by_branches(csv_path: str, output_base_dir: str, base_filename: str, analytics_dir: str = None) -> tuple:
    """Split CSV file by branches into separate files."""
    validate_csv_input(csv_path)
    branches, timing_stats = get_branches(), {}
    try:
        return execute_split(csv_path, output_base_dir, base_filename, analytics_dir, branches, timing_stats)
    except (FileNotFoundError, ValueError):
        raise
    except Exception as error:
        logger.exception("Error splitting CSV: %s", error)
        raise ValueError(f"Error splitting CSV: {error}") from error

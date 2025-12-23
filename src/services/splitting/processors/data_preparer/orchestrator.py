"""Main orchestrator for data preparation."""

from src.core.domain.branches.config import get_base_columns, get_branches
from src.services.splitting.processors.data_preparer import (
    loading, dates, columns, processing
)


def prepare_branch_data(
    csv_path: str, start_date=None, end_date=None, require_dates=False
) -> tuple:
    """Prepare branch data from CSV file."""
    first_line = loading.read_first_line(csv_path)
    start_date, end_date, header_contained_dates = dates.resolve_date_range(
        first_line, start_date, end_date
    )
    num_days = dates.validate_date_range(start_date, end_date, require_dates)
    dataframe = loading.read_csv_with_header(csv_path, header_contained_dates)
    
    branches, base_columns = get_branches(), get_base_columns()
    columns.validate_required_columns(dataframe, branches, base_columns)
    
    return (
        processing.build_branch_data_dict(
            dataframe, branches, base_columns, num_days
        ), 
        header_contained_dates, 
        first_line
    )

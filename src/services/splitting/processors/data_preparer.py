"""Data preparation for branch splitting"""

import pandas as pd
from src.core.domain.branches.config import get_base_columns, get_branches
from src.core.domain.calculations.quantity_calculator import calculate_basic_quantities
from src.core.validation.data_validator import extract_dates_from_header, calculate_days_between
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Default number of days when no date information is available
DEFAULT_DAYS_FOR_AVG_SALES = 90


def _read_first_line(csv_path: str) -> str:
    """Read the first line from a CSV file."""
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        return f.readline().strip()


def _resolve_date_range(first_line: str, start_date, end_date) -> tuple:
    """
    Resolve date range from parameters or header.
    
    Returns:
        Tuple of (start_date, end_date, header_contained_dates)
    """
    extracted_start, extracted_end = extract_dates_from_header(first_line)
    header_contained_dates = bool(extracted_start and extracted_end)
    
    if start_date is None:
        start_date = extracted_start
    if end_date is None:
        end_date = extracted_end
    
    return start_date, end_date, header_contained_dates


def _validate_date_range(start_date, end_date, require_dates: bool) -> int:
    """
    Validate date range and calculate number of days.
    
    Returns:
        Number of days in the range
        
    Raises:
        ValueError: If dates are invalid or required but missing
    """
    has_date_info = bool(start_date and end_date)
    
    if require_dates and not has_date_info:
        raise ValueError(
            "❌ خطأ: لم يتم العثور على معلومات التاريخ!\n"
            "يجب توفير التواريخ إما:\n"
            "1. في السطر الأول من الملف بالصيغة: من: DD/MM/YYYY HH:MM إلى: DD/MM/YYYY HH:MM\n"
            "2. أو تمريرها كمعاملات (start_date, end_date)"
        )
    
    if has_date_info:
        num_days = calculate_days_between(start_date, end_date)
        if num_days <= 0:
            raise ValueError(
                f"❌ خطأ: نطاق التاريخ غير صالح!\n"
                f"تاريخ البداية: {start_date}\n"
                f"تاريخ النهاية: {end_date}"
            )
        logger.info(f"✅ Date range: {num_days} days from {start_date} to {end_date}")
        return num_days
    
    logger.warning(f"⚠️ No date information found. Using default: {DEFAULT_DAYS_FOR_AVG_SALES} days")
    return DEFAULT_DAYS_FOR_AVG_SALES


def _read_csv_with_header(csv_path: str, header_contained_dates: bool) -> pd.DataFrame:
    """Read CSV file, skipping date header if present."""
    if header_contained_dates:
        df = pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig')
    else:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    if df.empty:
        raise ValueError("CSV file contains no data")
    
    return df


def _validate_required_columns(df: pd.DataFrame, branches: list, base_columns: list) -> None:
    """Validate that all required columns exist in the DataFrame."""
    required_columns = set(base_columns)
    for branch in branches:
        required_columns.update([f'{branch}_sales', f'{branch}_balance'])
    
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def _create_branch_dataframe(df: pd.DataFrame, branch: str, base_columns: list, num_days: int) -> pd.DataFrame:
    """Create a processed DataFrame for a single branch."""
    branch_cols = [f'{branch}_sales', f'{branch}_balance']
    selected_columns = base_columns + branch_cols
    branch_df = df[selected_columns].copy()
    
    branch_df.columns = base_columns + ['sales', 'balance']
    branch_df['sales'] = pd.to_numeric(branch_df['sales'], errors='coerce').fillna(0.0)
    branch_df['balance'] = pd.to_numeric(branch_df['balance'], errors='coerce').fillna(0.0)
    branch_df['avg_sales'] = branch_df['sales'] / num_days
    
    return calculate_basic_quantities(branch_df)


def prepare_branch_data(csv_path: str, start_date=None, end_date=None, require_dates=False) -> tuple:
    """
    Prepare branch data from CSV file.
    
    Args:
        csv_path: Input CSV file path
        start_date: Optional start date
        end_date: Optional end date
        require_dates: If True, raise error if no dates found
        
    Returns:
        Tuple of (branch_data dict, has_date_header bool, first_line str)
    """
    first_line = _read_first_line(csv_path)
    start_date, end_date, header_contained_dates = _resolve_date_range(first_line, start_date, end_date)
    num_days = _validate_date_range(start_date, end_date, require_dates)
    
    df = _read_csv_with_header(csv_path, header_contained_dates)
    
    branches = get_branches()
    base_columns = get_base_columns()
    _validate_required_columns(df, branches, base_columns)
    
    branch_data = {}
    for branch in branches:
        branch_data[branch] = _create_branch_dataframe(df, branch, base_columns, num_days)
        logger.info(f"✅ Calculated avg_sales for {branch}: sales / {num_days} days")
    
    logger.info("Prepared data for %d branches, %d products", len(branches), len(branch_data[branches[0]]))
    
    return branch_data, header_contained_dates, first_line



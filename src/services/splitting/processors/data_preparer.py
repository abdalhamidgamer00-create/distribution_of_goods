"""Data preparation for branch splitting"""

import pandas as pd
from src.core.domain.branches.config import get_base_columns, get_branches
from src.core.domain.calculations.quantity_calculator import calculate_basic_quantities
from src.core.validation.data_validator import extract_dates_from_header
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def prepare_branch_data(csv_path: str) -> tuple:
    """
    Prepare branch data from CSV file
    
    Args:
        csv_path: Input CSV file path
        
    Returns:
        Tuple of (branch_data dict, has_date_header bool, first_line str)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
    """
    # قراءة السطر الأول
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline().strip()
    
    # التحقق من وجود تاريخ في الرأس
    start_date, end_date = extract_dates_from_header(first_line)
    has_date_header = bool(start_date and end_date)
    
    # قراءة CSV
    if has_date_header:
        df = pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig')
    else:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # التحقق من وجود البيانات
    if df.empty:
        raise ValueError("CSV file contains no data")
    
    branches = get_branches()
    base_columns = get_base_columns()
    branch_data = {}
    
    # التحقق من وجود جميع الأعمدة المطلوبة
    required_columns = set(base_columns)
    for branch in branches:
        required_columns.update([
            f'{branch}_sales', 
            f'{branch}_avg_sales', 
            f'{branch}_balance'
        ])
    
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # تحضير البيانات لكل فرع
    for branch in branches:
        branch_columns = [
            f'{branch}_sales', 
            f'{branch}_avg_sales', 
            f'{branch}_balance'
        ]
        selected_columns = base_columns + branch_columns
        
        branch_df = df[selected_columns].copy()
        branch_df.columns = base_columns + ['sales', 'avg_sales', 'balance']
        branch_df = calculate_basic_quantities(branch_df)
        branch_data[branch] = branch_df
    
    logger.info("Prepared data for %d branches, %d products", 
                len(branches), len(branch_data[branches[0]]))
    
    return branch_data, has_date_header, first_line


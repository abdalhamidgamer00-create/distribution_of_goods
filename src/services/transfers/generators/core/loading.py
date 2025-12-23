"""Analytics loading logic for transfer generation."""

import os
import pandas as pd
from src.shared.dataframes.validators import ensure_columns
from src.shared.utils.file_handler import get_latest_file


def load_analytics_file(analytics_path: str) -> pd.DataFrame:
    """Load and validate analytics file."""
    dataframe = pd.read_csv(analytics_path, encoding='utf-8-sig')
    ensure_columns(
        dataframe, 
        ["code", "product_name"], 
        context=f"analytics file {analytics_path}"
    )
    return dataframe


def find_analytics_file(target_analytics_dir: str) -> str:
    """Find latest analytics file in directory."""
    if not os.path.exists(target_analytics_dir):
        return None
    return get_latest_file(target_analytics_dir, '.csv')


def get_analytics_path(analytics_dir: str, target_branch: str) -> tuple:
    """Get analytics file path and base name."""
    target_analytics_dir = os.path.join(analytics_dir, target_branch)
    latest_analytics_file = find_analytics_file(target_analytics_dir)
    
    if not latest_analytics_file:
        return None, None, None
    
    analytics_path = os.path.join(target_analytics_dir, latest_analytics_file)
    base_name = os.path.splitext(latest_analytics_file)[0].replace(
        f'_{target_branch}_analytics', ''
    )
    return analytics_path, latest_analytics_file, base_name

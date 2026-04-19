"""Score calculation helpers."""

import pandas as pd
from .allocation_constants import (
    AVERAGE_DAILY_SALES_WEIGHT, NEEDED_WEIGHT, BALANCE_WEIGHT
)


def normalize_scores(series: pd.Series) -> pd.Series:
    """Normalize series to 0-1 range."""
    min_value, max_value = series.min(), series.max()
    if max_value - min_value == 0:
        return pd.Series([1.0] * len(series), index=series.index)
    return (series - min_value) / (max_value - min_value)


def calculate_weighted_scores(matrices: dict, product_index: int) -> pd.Series:
    """Calculate weighted priority scores for each branch."""
    average_daily_sales_scores = matrices['average_daily_sales'].loc[product_index].clip(lower=0)
    needed_scores = matrices['needed'].loc[product_index].clip(lower=0)
    inverse_balance_scores = 1.0 / (
        matrices['balance'].loc[product_index] + 0.1
    )
    
    return (
        AVERAGE_DAILY_SALES_WEIGHT * normalize_scores(average_daily_sales_scores) +
        NEEDED_WEIGHT * normalize_scores(needed_scores) +
        BALANCE_WEIGHT * normalize_scores(inverse_balance_scores)
    )

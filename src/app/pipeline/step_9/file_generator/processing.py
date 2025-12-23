"""Processing helpers for file generation."""

import pandas as pd
from src.core.domain.classification.product_classifier import classify_product_type


def add_product_type_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Add product_type column based on product_name."""
    dataframe = dataframe.copy()
    dataframe['product_type'] = dataframe['product_name'].apply(classify_product_type)
    return dataframe


def process_category_dataframe(dataframe: pd.DataFrame, category: str) -> pd.DataFrame:
    """Filter, sort and clean category DataFrame."""
    category_dataframe = dataframe[dataframe['product_type'] == category].copy()
    
    if len(category_dataframe) == 0:
        return None
    
    category_dataframe = category_dataframe.sort_values(
        'product_name', ascending=True, key=lambda column: column.str.lower()
    )
    return category_dataframe.drop('product_type', axis=1)

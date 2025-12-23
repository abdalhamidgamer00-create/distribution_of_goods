"""Data processing and transformation for shortage generation."""

import pandas as pd


def prepare_category_dataframe(
    shortage_dataframe: pd.DataFrame, 
    category: str
) -> pd.DataFrame:
    """Prepare category dataframe for output."""
    category_dataframe = shortage_dataframe[
        shortage_dataframe['product_type'] == category
    ].copy()
    
    if len(category_dataframe) == 0:
        return None
        
    return category_dataframe.sort_values(
        'shortage_quantity', ascending=False
    ).drop('product_type', axis=1)

"""Classification helpers."""
import pandas as pd
from .constants import PRODUCT_TYPE_KEYWORDS

def classify_by_keywords(unit: str, product_name: str) -> str:
    """Classify product based on unit and product name keywords."""
    for category, (unit_keywords, name_keywords) in PRODUCT_TYPE_KEYWORDS.items():
        if any(keyword in unit for keyword in unit_keywords):
            return category
        if any(keyword in product_name for keyword in name_keywords):
            return category
    return 'other'


def add_product_type_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add product_type column based on unit type."""
    df = df.copy()
    
    def classify_product(row):
        unit = str(row.get('unit', '')).lower() if 'unit' in row else ''
        product_name = str(row.get('product_name', '')).lower()
        return classify_by_keywords(unit, product_name)
    
    df['product_type'] = df.apply(classify_product, axis=1)
    return df

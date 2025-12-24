"""Service for extracting product information from raw data."""

from typing import List, Optional
import pandas as pd
from src.domain.models.entities import Product


class ProductExtractor:
    """Handles the identification and extraction of product codes and names."""

    @staticmethod
    def extract(row: pd.Series) -> Optional[Product]:
        """Extracts validated product information from a data series."""
        code_keys = ['code', 'كود', 'كود الصنف', 'item code', 'item_code']
        name_keys = ['product_name', 'إسم الصنف', 'اسم الصنف', 'item name']
        
        item_code = str(ProductExtractor._lookup(row, code_keys)).strip()
        item_name = str(ProductExtractor._lookup(row, name_keys)).strip()

        if not item_code or item_code == 'nan' or \
           not item_name or item_name == 'nan':
            return None
        return Product(code=item_code, name=item_name)

    @staticmethod
    def _lookup(row: pd.Series, keys: List[str]) -> str:
        """Searches for a value using multiple fallback keys."""
        for key in keys:
            if key in row:
                return row[key]
        
        normalized_keys = [k.strip().lower() for k in keys]
        for column_name in row.index:
            cl_col = str(column_name).strip().lower().replace('\ufeff', '')
            if cl_col in normalized_keys:
                return row[column_name]
        return ""

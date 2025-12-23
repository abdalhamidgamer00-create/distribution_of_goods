"""Mapper for converting between domain models and data structures."""

import math
import pandas as pd
from typing import Dict, List, Optional
from src.domain.models.entities import (
    Product, StockLevel, ConsolidatedStock, BranchStock
)
from src.shared.constants import BRANCHES


class StockMapper:
    """Handles mapping between domain models and Pandas data representations."""

    @staticmethod
    def to_consolidated_stock(row_data: pd.Series, num_days: int) -> Optional[ConsolidatedStock]:
        """Map a Pandas row to a ConsolidatedStock domain object with flexible lookup and validation."""
        def get_value(search_keys: List[str], default_value=""):
            # 1. Try exact matches first
            for search_key in search_keys:
                if search_key in row_data:
                    return row_data[search_key]
            
            # 2. Try case-insensitive and stripped lookup as fallback
            for search_key in search_keys:
                normalized_target = search_key.strip().lower()
                for existing_row_key in row_data.index:
                    clean_row_key = str(existing_row_key).strip().lower().replace('\ufeff', '')
                    if normalized_target == clean_row_key:
                        return row_data[existing_row_key]
            return default_value

        code_value = str(get_value(['code', 'كود', 'كود الصنف', 'item code', 'item_code'])).strip()
        name_value = str(get_value(['product_name', 'إسم الصنف', 'اسم الصنف', 'item name', 'item_name'])).strip()

        # Skip rows with no code or name (often artifacts of empty Excel rows or bad header reads)
        if not code_value or code_value == 'nan' or not name_value or name_value == 'nan':
            return None

        product_entity = Product(code=code_value, name=name_value)
        
        branch_stock_levels = {}
        # Possible variations for sales and balance
        sales_column_suffixes = ["_sales", " مبيعات", "مبيعات "]
        balance_column_suffixes = ["_balance", " رصيد", "رصيد "]

        for branch in BRANCHES:
            # Try to find sales column
            sales_value = 0.0
            for suffix in sales_column_suffixes:
                column_key = f"{branch}{suffix}" if "_" in suffix else f"{suffix}{branch}"
                if column_key in row_data:
                    sales_value = pd.to_numeric(row_data[column_key], errors='coerce') or 0.0
                    break
            
            # Try to find balance column
            balance_value = 0.0
            for suffix in balance_column_suffixes:
                column_key = f"{branch}{suffix}" if "_" in suffix else f"{suffix}{branch}"
                if column_key in row_data:
                    balance_value = pd.to_numeric(row_data[column_key], errors='coerce') or 0.0
                    break
            
            average_daily_sales = sales_value / num_days if num_days > 0 else 0.0
            monthly_needed_quantity = math.ceil(average_daily_sales * 30)
            
            surplus_quantity = math.floor(max(0, balance_value - monthly_needed_quantity))
            needed_quantity = math.ceil(max(0, monthly_needed_quantity - balance_value))
            
            branch_stock_levels[branch] = StockLevel(
                needed=needed_quantity,
                surplus=surplus_quantity,
                balance=float(balance_value),
                avg_sales=float(average_daily_sales),
                sales=float(sales_value)
            )
            
        return ConsolidatedStock(product=product_entity, branch_stocks=branch_stock_levels)

    @staticmethod
    def to_stock_level(row: pd.Series) -> StockLevel:
        """Map a branch analysis row back to a StockLevel domain object."""
        return StockLevel(
            needed=int(row['needed_quantity']),
            surplus=int(row['surplus_quantity']),
            balance=float(row['balance']),
            avg_sales=float(row['avg_sales']),
            sales=float(row.get('sales', 0.0))
        )

    @staticmethod
    def to_branch_dataframe(stocks_list: List[BranchStock]) -> pd.DataFrame:
        """Map a list of BranchStock to a Pandas DataFrame for saving."""
        mapped_data = []
        for branch_stock in stocks_list:
            mapped_data.append({
                'code': branch_stock.product.code,
                'product_name': branch_stock.product.name,
                'sales': branch_stock.stock.sales,
                'balance': branch_stock.stock.balance,
                'avg_sales': branch_stock.stock.avg_sales,
                'needed_quantity': branch_stock.stock.needed,
                'surplus_quantity': branch_stock.stock.surplus
            })
        return pd.DataFrame(mapped_data)

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
    def to_consolidated_stock(row: pd.Series, num_days: int) -> Optional[ConsolidatedStock]:
        """Map a Pandas row to a ConsolidatedStock domain object with flexible lookup and validation."""
        def get_val(keys: List[str], default=""):
            # 1. Try exact matches first
            for k in keys:
                if k in row:
                    return row[k]
            
            # 2. Try case-insensitive and stripped lookup as fallback
            for k in keys:
                target = k.strip().lower()
                for row_key in row.index:
                    rk = str(row_key).strip().lower().replace('\ufeff', '')
                    if target == rk:
                        return row[row_key]
            return default

        code_val = str(get_val(['code', 'كود', 'كود الصنف', 'item code', 'item_code'])).strip()
        name_val = str(get_val(['product_name', 'إسم الصنف', 'اسم الصنف', 'item name', 'item_name'])).strip()

        # Skip rows with no code or name (often artifacts of empty Excel rows or bad header reads)
        if not code_val or code_val == 'nan' or not name_val or name_val == 'nan':
            return None

        product = Product(code=code_val, name=name_val)
        
        branch_stocks = {}
        # Possible variations for sales and balance
        sales_keys = ["_sales", " مبيعات", "مبيعات "]
        balance_keys = ["_balance", " رصيد", "رصيد "]

        for branch in BRANCHES:
            # Try to find sales column
            sales_val = 0.0
            for suffix in sales_keys:
                key = f"{branch}{suffix}" if "_" in suffix else f"{suffix}{branch}"
                if key in row:
                    sales_val = pd.to_numeric(row[key], errors='coerce') or 0.0
                    break
            
            # Try to find balance column
            balance_val = 0.0
            for suffix in balance_keys:
                key = f"{branch}{suffix}" if "_" in suffix else f"{suffix}{branch}"
                if key in row:
                    balance_val = pd.to_numeric(row[key], errors='coerce') or 0.0
                    break
            
            avg_sales = sales_val / num_days if num_days > 0 else 0.0
            monthly_qty = math.ceil(avg_sales * 30)
            
            surplus = math.floor(max(0, balance_val - monthly_qty))
            needed = math.ceil(max(0, monthly_qty - balance_val))
            
            branch_stocks[branch] = StockLevel(
                needed=needed,
                surplus=surplus,
                balance=float(balance_val),
                avg_sales=float(avg_sales),
                sales=float(sales_val)
            )
            
        return ConsolidatedStock(product=product, branch_stocks=branch_stocks)

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
    def to_branch_dataframe(stocks: List[BranchStock]) -> pd.DataFrame:
        """Map a list of BranchStock to a Pandas DataFrame for saving."""
        data = []
        for bs in stocks:
            data.append({
                'code': bs.product.code,
                'product_name': bs.product.name,
                'sales': bs.stock.sales,
                'balance': bs.stock.balance,
                'avg_sales': bs.stock.avg_sales,
                'needed_quantity': bs.stock.needed,
                'surplus_quantity': bs.stock.surplus
            })
        return pd.DataFrame(data)

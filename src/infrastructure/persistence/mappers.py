"""Mapper for converting between domain models and data structures."""

import math
import pandas as pd
from typing import Dict, List
from src.domain.models.entities import (
    Product, StockLevel, ConsolidatedStock, BranchStock
)
from src.shared.constants import BRANCHES


class StockMapper:
    """Handles mapping between domain models and Pandas data representations."""

    @staticmethod
    def to_consolidated_stock(row: pd.Series, num_days: int) -> ConsolidatedStock:
        """Map a Pandas row to a ConsolidatedStock domain object."""
        product = Product(
            code=str(row['code']),
            name=str(row['product_name'])
        )
        
        branch_stocks = {}
        for branch in BRANCHES:
            # Step 5 renames columns to {branch}_sales and {branch}_balance
            sales = pd.to_numeric(row[f"{branch}_sales"], errors='coerce') or 0.0
            balance = pd.to_numeric(row[f"{branch}_balance"], errors='coerce') or 0.0
            
            avg_sales = sales / num_days if num_days > 0 else 0.0
            monthly_qty = math.ceil(avg_sales * 30)
            
            surplus = math.floor(max(0, balance - monthly_qty))
            needed = math.ceil(max(0, monthly_qty - balance))
            
            branch_stocks[branch] = StockLevel(
                needed=needed,
                surplus=surplus,
                balance=float(balance),
                avg_sales=float(avg_sales),
                sales=float(sales)
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

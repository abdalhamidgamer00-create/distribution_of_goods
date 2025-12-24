"""Mapper for converting between domain models and data structures."""

import math
import pandas as pd
from typing import Dict, List, Optional
from src.domain.models.entities import (
    StockLevel, ConsolidatedStock, BranchStock
)
from src.shared.constants import BRANCHES
from src.infrastructure.repositories.product_extractor import ProductExtractor


class StockMapper:
    """Handles mapping between domain models and Pandas representations."""

    @staticmethod
    def to_consolidated_stock(
        row_data: pd.Series, 
        num_days: int
    ) -> Optional[ConsolidatedStock]:
        """Maps a row to a ConsolidatedStock domain object."""
        product = ProductExtractor.extract(row_data)
        if not product:
            return None

        branch_stocks = {}
        for branch in BRANCHES:
            stock_level = StockMapper._calculate_branch_stock(
                row_data, branch, num_days
            )
            branch_stocks[branch] = stock_level
            
        return ConsolidatedStock(
            product=product, branch_stocks=branch_stocks
        )

    @staticmethod
    def _calculate_branch_stock(
        row: pd.Series, 
        branch: str, 
        days: int
    ) -> StockLevel:
        """Calculates inventory needs and surpluses for a branch."""
        sales = StockMapper._find_metric(row, branch, ["_sales", " مبيعات"])
        balance = StockMapper._find_metric(row, branch, ["_balance", " رصيد"])
        
        daily_avg = sales / days if days > 0 else 0.0
        monthly_need = math.ceil(daily_avg * 30)
        
        surplus = math.floor(max(0, balance - monthly_need))
        needed = math.ceil(max(0, monthly_need - balance))
        
        return StockLevel(
            needed=needed, surplus=surplus, balance=float(balance),
            avg_sales=float(daily_avg), sales=float(sales)
        )

    @staticmethod
    def _find_metric(row: pd.Series, branch: str, suffixes: List[str]) -> float:
        """Finds a specific numeric metric for a branch in the row."""
        for suffix in suffixes:
            key = f"{branch}{suffix}" if "_" in suffix else f"{suffix}{branch}"
            if key in row:
                return pd.to_numeric(row[key], errors='coerce') or 0.0
        return 0.0

    @staticmethod
    def to_stock_level(row: pd.Series) -> StockLevel:
        """Maps a analysis row to a StockLevel domain object."""
        return StockLevel(
            needed=int(row['needed_quantity']),
            surplus=int(row['surplus_quantity']),
            balance=float(row['balance']),
            avg_sales=float(row['avg_sales']),
            sales=float(row.get('sales', 0.0))
        )

    @staticmethod
    def to_branch_dataframe(stocks: List[BranchStock]) -> pd.DataFrame:
        """Converts a list of BranchStock to a saving-ready DataFrame."""
        records = []
        for branch_stock in stocks:
            records.append({
                'code': branch_stock.product.code,
                'product_name': branch_stock.product.name,
                'sales': branch_stock.stock.sales,
                'balance': branch_stock.stock.balance,
                'avg_sales': branch_stock.stock.avg_sales,
                'needed_quantity': branch_stock.stock.needed,
                'surplus_quantity': branch_stock.stock.surplus
            })
        return pd.DataFrame(records)

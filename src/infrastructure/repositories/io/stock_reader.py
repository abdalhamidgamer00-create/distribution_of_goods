"""Specialized component for reading stock data from disk."""

import os
import pandas as pd
from typing import List, Dict, Optional
from src.domain.models.entities import Product, StockLevel, ConsolidatedStock
from src.infrastructure.repositories.mappers.mappers import StockMapper
from src.domain.services.validation.dates import extract_dates_from_header
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)


class StockReader:
    """Handles loading of stock-related data from CSV files."""

    def __init__(self, analytics_directory: str):
        self._analytics_directory = analytics_directory

    def load_consolidated_stock(self, csv_path: str) -> List[ConsolidatedStock]:
        """Loads and maps consolidated stock from a CSV file."""
        if not csv_path or not os.path.exists(csv_path):
            return []
            
        try:
            dataframe, days = self._read_csv_and_extract_days(csv_path)
            dataframe.columns = [
                column.strip().replace('\ufeff', '') 
                for column in dataframe.columns
            ]
            
            return self._map_dataframe_to_entities(dataframe, days)
        except Exception as error:
            logger.error(f"Error loading stock from {csv_path}: {error}")
            return []

    def load_stock_levels(
        self, branch_name: str, days: int = 90
    ) -> Dict[str, StockLevel]:
        """Reads branch-specific stock levels from disk."""
        path = os.path.join(
            self._analytics_directory, 
            branch_name, 
            f"main_analysis_{branch_name}.csv"
        )
        if not os.path.exists(path):
            return {}
            
        try:
            dataframe = pd.read_csv(path, encoding='utf-8-sig')
            return self._parse_stocks_dataframe(dataframe, days)
        except Exception as error:
            logger.error(f"Error loading levels for {branch_name}: {error}")
            return {}

    def _read_csv_and_extract_days(self, path: str) -> tuple[pd.DataFrame, int]:
        """Reads CSV and extracts total days from date header."""
        from src.domain.services.validation.dates import (
            extract_dates_from_header, calculate_days_between
        )
        
        with open(path, 'r', encoding='utf-8-sig') as file:
            first_line = file.readline().strip()
        
        start_date, end_date = extract_dates_from_header(first_line)
        days = 90 # Default fallback
        skip = 0
        
        if start_date and end_date:
            days = calculate_days_between(start_date, end_date)
            skip = 1
        else:
            # Fallback check for unnamed columns or Arabic headers
            dataframe_head = pd.read_csv(path, encoding='utf-8-sig', nrows=5)
            first_column = dataframe_head.columns[0]
            if first_column.startswith('Unnamed') or 'الفترة من' in first_column:
                skip = 1

        dataframe = pd.read_csv(path, skiprows=skip, encoding='utf-8-sig')
        return dataframe, days

    def _map_dataframe_to_entities(
        self, 
        dataframe: pd.DataFrame,
        days: int
    ) -> List[ConsolidatedStock]:
        """Maps pandas dataframe rows to domain entities."""
        results = []
        for _, row in dataframe.iterrows():
            object_instance = StockMapper.to_consolidated_stock(row, days)
            if object_instance:
                results.append(object_instance)
        return results

    def _parse_stocks_dataframe(
        self, 
        dataframe: pd.DataFrame,
        days: int
    ) -> Dict[str, StockLevel]:
        """Parses a dataframe into a dictionary of StockLevel objects."""
        stocks = {}
        for _, row in dataframe.iterrows():
            code_column = 'code' if 'code' in row else 'كود'
            if code_column in row:
                stocks[str(row[code_column])] = StockMapper.to_stock_level(
                    row, days
                )
        return stocks

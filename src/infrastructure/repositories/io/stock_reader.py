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
            dataframe = self._read_csv_with_header(csv_path)
            dataframe.columns = [
                column.strip().replace('\ufeff', '') 
                for column in dataframe.columns
            ]
            
            return self._map_dataframe_to_entities(dataframe)
        except Exception as error:
            logger.error(f"Error loading stock from {csv_path}: {error}")
            return []

    def load_stock_levels(self, branch_name: str) -> Dict[str, StockLevel]:
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
            return self._parse_stocks_dataframe(dataframe)
        except Exception as error:
            logger.error(f"Error loading levels for {branch_name}: {error}")
            return {}

    def _read_csv_with_header(self, path: str) -> pd.DataFrame:
        """Reads CSV and handles optional 1-line date header."""
        with open(path, 'r', encoding='utf-8-sig') as file:
            first_line = file.readline().strip()
        
        start_date, end_date = extract_dates_from_header(first_line)
        if start_date and end_date:
            return pd.read_csv(path, skiprows=1, encoding='utf-8-sig')
        
        dataframe_head = pd.read_csv(path, encoding='utf-8-sig', nrows=5)
        first_column = dataframe_head.columns[0]
        if first_column.startswith('Unnamed') or 'الفترة من' in first_column:
            return pd.read_csv(path, skiprows=1, encoding='utf-8-sig')

        return pd.read_csv(path, encoding='utf-8-sig')

    def _map_dataframe_to_entities(
        self, 
        dataframe: pd.DataFrame
    ) -> List[ConsolidatedStock]:
        """Maps pandas dataframe rows to domain entities."""
        results = []
        for _, row in dataframe.iterrows():
            object_instance = StockMapper.to_consolidated_stock(row, 90)
            if object_instance:
                results.append(object_instance)
        return results

    def _parse_stocks_dataframe(
        self, 
        dataframe: pd.DataFrame
    ) -> Dict[str, StockLevel]:
        """Parses a dataframe into a dictionary of StockLevel objects."""
        stocks = {}
        for _, row in dataframe.iterrows():
            code_column = 'code' if 'code' in row else 'كود'
            if code_column in row:
                stocks[str(row[code_column])] = StockMapper.to_stock_level(row)
        return stocks

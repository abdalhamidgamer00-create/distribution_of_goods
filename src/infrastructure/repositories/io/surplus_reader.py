"""Specialized component for reading surplus data from disk."""

import os
import pandas as pd
from typing import List, Dict
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)


class SurplusReader:
    """Handles loading of surplus reports for inventory management."""

    def __init__(self, surplus_directory: str):
        self._surplus_directory = surplus_directory

    def load_remaining_surplus(self, branch_name: str) -> List[Dict]:
        """Loads total surplus records for a specific branch from disk."""
        directory = os.path.join(self._surplus_directory, "csv", branch_name)
        if not os.path.exists(directory):
            return []
            
        records = []
        for filename in os.listdir(directory):
            if self._is_surplus_file(filename):
                path = os.path.join(directory, filename)
                records.extend(self._parse_surplus_csv(path))
        return records

    def _is_surplus_file(self, name: str) -> bool:
        """Identifies official Step 9 total surplus CSV files."""
        return (
            name.endswith('.csv') and 
            'remaining_surplus' in name and 
            '_total_' in name
        )

    def _parse_surplus_csv(self, path: str) -> List[Dict]:
        """Parses a surplus CSV into a list of dictionaries for the UI."""
        try:
            dataframe = pd.read_csv(path, encoding='utf-8-sig')
            results = []
            for _, row in dataframe.iterrows():
                results.append({
                    'code': str(row['code']),
                    'product_name': row['product_name'],
                    'quantity': int(row['remaining_surplus']),
                    'target_branch': 'administration',
                    'transfer_type': 'surplus'
                })
            return results
        except Exception as error:
            logger.error(f"Error reading surplus {path}: {error}")
            return []

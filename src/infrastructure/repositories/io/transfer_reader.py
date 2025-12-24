"""Specialized component for reading transfer data from disk."""

import os
import pandas as pd
from typing import List
from src.domain.models.entities import Product, Branch
from src.domain.models.distribution import Transfer
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)


class TransferReader:
    """Handles discovery and parsing of transfer-related CSV files."""

    def __init__(self, output_directory: str):
        self._output_directory = output_directory

    def walk_for_transfers(self) -> List[Transfer]:
        """Recursive walk to find and parse transfer files."""
        transfers = []
        if not os.path.exists(self._output_directory):
            return []
            
        for root, _, files in os.walk(self._output_directory):
            for filename in files:
                if self._is_transfer_file(filename):
                    path = os.path.join(root, filename)
                    transfers.extend(self._parse_transfer_file(path, filename))
        return transfers

    def _is_transfer_file(self, filename: str) -> bool:
        """Determines if a file is a valid Step 7 transfer CSV."""
        is_csv = filename.endswith('.csv')
        is_transfer = '_to_' in filename
        is_split = any(category in filename for category in [
            "tablets", "injections", "syrups", "creams", "sachets", "other"
        ])
        return is_csv and is_transfer and not is_split

    def _parse_transfer_file(self, path: str, name: str) -> List[Transfer]:
        """Parses a single transfer CSV file into domain objects."""
        base_name = os.path.splitext(name)[0]
        name_parts = base_name.split('_to_')
        if len(name_parts) < 2:
            return []
            
        source_branch = name_parts[0].split('_')[-1]
        target_branch = name_parts[1].split('_')[0]
        
        try:
            dataframe = pd.read_csv(path, encoding='utf-8-sig')
            return self._map_rows_to_transfers(
                dataframe, source_branch, target_branch
            )
        except Exception as error:
            logger.error(f"Error parsing transfer file {path}: {error}")
            return []

    def _map_rows_to_transfers(
        self, 
        dataframe: pd.DataFrame, 
        source: str, 
        target: str
    ) -> List[Transfer]:
        """Maps dataframe rows to Transfer domain objects."""
        results = []
        for _, row in dataframe.iterrows():
            results.append(Transfer(
                product=Product(
                    code=str(row['code']), 
                    name=row['product_name']
                ),
                from_branch=Branch(name=source),
                to_branch=Branch(name=target),
                quantity=int(row['quantity_to_transfer'])
            ))
        return results

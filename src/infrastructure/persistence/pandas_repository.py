"""Pandas implementation of the DataRepository interface."""

import os
import pandas as pd
from typing import List, Dict, Optional
from src.domain.models.entities import (
    Product, Branch, StockLevel, ConsolidatedStock, BranchStock
)
from src.domain.models.distribution import Transfer, DistributionResult
from src.infrastructure.persistence.mappers import StockMapper
from src.shared.utils.logging_utils import get_logger
from src.shared.constants import BRANCHES
from src.application.interfaces.repository import DataRepository
from src.core.validation.dates import extract_dates_from_header

# Modular Helpers
from src.infrastructure.persistence.transfers_persistence import (
    save_step7_transfers, save_step8_split_transfers
)
from src.infrastructure.persistence.reports_persistence import (
    save_surplus_reports, save_shortage_reports
)
from src.infrastructure.persistence.combined_transfers_persistence import (
    save_step11_combined_transfers
)
from src.infrastructure.persistence.output_manager import list_artifacts

logger = get_logger(__name__)


class PandasDataRepository(DataRepository):
    """Handles data persistence using Pandas and local files."""

    def __init__(self, input_dir: str, output_dir: str, **kwargs):
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._surplus_dir = kwargs.get('surplus_dir', output_dir)
        self._shortage_dir = kwargs.get('shortage_dir', output_dir)
        self._analytics_dir = kwargs.get('analytics_dir', output_dir)
        self._transfers_dir = kwargs.get('transfers_dir', output_dir)

    def load_branches(self) -> List[Branch]:
        """Loads available branches from constants."""
        return [Branch(name=name) for name in BRANCHES]

    def load_products(self) -> List[Product]:
        """Loads unique products from consolidated stock."""
        consolidated = self.load_consolidated_stock()
        return [item.product for item in consolidated]

    def load_consolidated_stock(self) -> List[ConsolidatedStock]:
        """Loads and maps consolidated stock from latest input CSV."""
        csv_path = self._get_latest_input_file()
        if not csv_path:
            return []
            
        try:
            df = self._read_csv_with_header_detection(csv_path)
            df.columns = [c.strip().replace('\ufeff', '') for c in df.columns]
            
            results = []
            for _, row in df.iterrows():
                obj = StockMapper.to_consolidated_stock(row, 90)
                if obj:
                    results.append(obj)
            return results
        except Exception as error:
            logger.error(f"Error loading stock from {csv_path}: {error}")
            return []

    def save_branch_stocks(self, branch: Branch, stocks: List[BranchStock]) -> None:
        """Saves branch-specific stock levels to CSV."""
        df = StockMapper.to_branch_dataframe(stocks)
        branch_dir = os.path.join(self._analytics_dir, branch.name)
        os.makedirs(branch_dir, exist_ok=True)
        
        path = os.path.join(branch_dir, f"main_analysis_{branch.name}.csv")
        df.to_csv(path, index=False, encoding='utf-8-sig')

    def load_stock_levels(self, branch: Branch) -> Dict[str, StockLevel]:
        """Loads stock levels for a specific branch."""
        path = os.path.join(self._analytics_dir, branch.name, f"main_analysis_{branch.name}.csv")
        if not os.path.exists(path):
            return {}
            
        try:
            df = pd.read_csv(path, encoding='utf-8-sig')
            stocks = {}
            for _, row in df.iterrows():
                code_col = 'code' if 'code' in row else 'كود'
                if code_col in row:
                    stocks[str(row[code_col])] = StockMapper.to_stock_level(row)
            return stocks
        except Exception as error:
            logger.error(f"Error loading levels for {branch.name}: {error}")
            return {}

    def save_transfers(self, transfers_list: List[Transfer]) -> None:
        """Saves transfers to CSV files (Step 7)."""
        os.makedirs(self._transfers_dir, exist_ok=True)
        save_step7_transfers(transfers_list, self._output_dir)

    def save_remaining_surplus(self, results: List[DistributionResult]) -> None:
        """Saves products with remaining surplus (Step 9)."""
        save_surplus_reports(results, self._surplus_dir)

    def save_shortage_report(self, results: List[DistributionResult]) -> None:
        """Saves products with a net shortage (Step 10)."""
        save_shortage_reports(results, self._shortage_dir)

    def load_transfers(self) -> List[Transfer]:
        """Loads transfers from the Step 7 output directory."""
        all_transfers = []
        if not os.path.exists(self._output_dir):
            return []
            
        for root, _, files in os.walk(self._output_dir):
            for filename in files:
                if filename.endswith('.csv') and '_to_' in filename:
                    if self._is_step8_split_file(filename):
                        continue
                    path = os.path.join(root, filename)
                    all_transfers.extend(self._parse_transfer_file(path, filename))
        return all_transfers

    def save_split_transfers(self, transfers_list: List[Transfer], excel_directory: str) -> None:
        """Saves transfers split by category (Step 8)."""
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_step8_split_transfers(transfers_list, self._output_dir, excel_directory, ts)

    def load_remaining_surplus(self, branch: Branch) -> List[Dict]:
        """Loads remaining surplus for a branch (Step 9 output)."""
        branch_dir = os.path.join(self._surplus_dir, branch.name)
        if not os.path.exists(branch_dir):
            return []
            
        data = []
        for file in os.listdir(branch_dir):
            if file.endswith('.csv') and 'remaining_surplus' in file:
                path = os.path.join(branch_dir, file)
                data.extend(self._read_surplus_csv(path))
        return data

    def save_combined_transfers(
        self, 
        branch: Branch, 
        merged_data_list: List[Dict], 
        separate_data_list: List[Dict], 
        timestamp_string: str
    ) -> None:
        """Saves combined transfers with Excel formatting (Step 11)."""
        save_step11_combined_transfers(
            branch, 
            merged_data_list, 
            separate_data_list, 
            timestamp_string
        )

    def list_outputs(self, category_name: str, branch_name_filter: Optional[str] = None) -> List[Dict]:
        """Lists available output artifacts for a category."""
        mapping = self._get_output_category_mapping()
        if category_name not in mapping:
            return []
            
        config = mapping[category_name]
        return list_artifacts(
            category_name, 
            config['base_directory'], 
            config['search_patterns'],
            branch_name_filter
        )

    def _get_latest_input_file(self) -> Optional[str]:
        """Finds the most recent renamed CSV in input directory."""
        if not os.path.exists(self._input_dir):
            return None
        files = [f for f in os.listdir(self._input_dir) if f.endswith('.csv')]
        if not files:
            return None
        files.sort(
            key=lambda f: os.path.getmtime(os.path.join(self._input_dir, f)),
            reverse=True
        )
        return os.path.join(self._input_dir, files[0])

    def _read_csv_with_header_detection(self, path: str) -> pd.DataFrame:
        """Reads CSV and handles optional 1-line date header."""
        with open(path, 'r', encoding='utf-8-sig') as f:
            first = f.readline().strip()
        
        start, end = extract_dates_from_header(first)
        if start and end:
            return pd.read_csv(path, skiprows=1, encoding='utf-8-sig')
        
        df_head = pd.read_csv(path, encoding='utf-8-sig', nrows=5)
        if (df_head.columns[0].startswith('Unnamed') or 
            'الفترة من' in df_head.columns[0]):
            return pd.read_csv(path, skiprows=1, encoding='utf-8-sig')

        return pd.read_csv(path, encoding='utf-8-sig')

    def _is_step8_split_file(self, filename: str) -> bool:
        """Checks if a filename indicates a Step 8 category-split file."""
        cats = ["tablets", "injections", "syrups", "creams", "sachets", "other"]
        return any(c in filename for c in cats)

    def _parse_transfer_file(self, path: str, name: str) -> List[Transfer]:
        """Parses a single transfer CSV file into domain objects."""
        base = os.path.splitext(name)[0]
        parts = base.split('_to_')
        if len(parts) < 2:
            return []
            
        src = parts[0].split('_')[-1]
        tgt = parts[1].split('_')[0]
        
        results = []
        try:
            df = self._read_csv_with_header_detection(path)
            for _, row in df.iterrows():
                results.append(Transfer(
                    product=Product(code=str(row['code']), name=row['product_name']),
                    from_branch=Branch(name=src),
                    to_branch=Branch(name=tgt),
                    quantity=int(row['quantity_to_transfer'])
                ))
        except Exception as e:
            logger.error(f"Error parsing transfer file {path}: {e}")
        return results

    def _read_surplus_csv(self, path: str) -> List[Dict]:
        """Reads a surplus CSV and formats for UI consumption."""
        results = []
        try:
            df = pd.read_csv(path, encoding='utf-8-sig')
            for _, row in df.iterrows():
                results.append({
                    'code': str(row['code']),
                    'product_name': row['product_name'],
                    'quantity': int(row['remaining_surplus']),
                    'target_branch': 'admin',
                    'transfer_type': 'surplus'
                })
        except Exception as e:
            logger.error(f"Error reading surplus {path}: {e}")
        return results

    def _get_output_category_mapping(self) -> Dict:
        """Returns internal configuration for listing artifacts."""
        return {
            'transfers': {
                'base_directory': self._output_dir,
                'search_patterns': {'csv': '', 'excel': ''}
            },
            'surplus': {
                'base_directory': self._surplus_dir,
                'search_patterns': {'csv': '', 'excel': ''}
            },
            'shortage': {
                'base_directory': self._shortage_dir,
                'search_patterns': {'csv': '', 'excel': ''}
            },
            'merged': {
                'base_directory': "data/output/combined_transfers/merged",
                'search_patterns': {
                    'csv': 'combined_transfers_from_', 
                    'excel': 'combined_transfers_from_'
                }
            },
            'separate': {
                'base_directory': "data/output/combined_transfers/separate",
                'search_patterns': {
                    'csv': 'transfers_from_', 
                    'excel': 'transfers_from_'
                }
            }
        }

"""Use case for generating combined transfer files with surplus."""

import pandas as pd
from typing import List, Dict, Any
from src.application.interfaces.repository import DataRepository
from src.domain.models.entities import Branch
from src.domain.models.distribution import Transfer
from src.core.domain.classification.product_classifier import classify_product_type

class GenerateCombinedTransfers:
    """
    Orchestrates the combination of transfers and surplus into
    formatted reports with balance information.
    """

    def __init__(self, repository: DataRepository, timestamp: str):
        self._repository = repository
        self._timestamp = timestamp

    def execute(self) -> tuple:
        """
        Executes the combination process for all branches.
        Returns (total_merged, total_separate) counts.
        """
        branches = self._repository.load_branches()
        total_merged = 0
        total_separate = 0
        
        # Pre-load transfers once
        all_transfers = self._repository.load_transfers()
        
        # Cache for stock levels to avoid redundant disk I/O
        stock_cache = {}
        
        for branch in branches:
            if branch.name == 'admin':
                continue
                
            merged_count, separate_count = self.execute_for_branch(branch, all_transfers, stock_cache)
            total_merged += merged_count
            total_separate += separate_count
        
        return total_merged, total_separate

    def execute_for_branch(self, branch: Branch, all_transfers: List[Transfer] = None, stock_cache: Dict = None) -> tuple:
        """Executes combination for a single branch."""
        if all_transfers is None:
            all_transfers = self._repository.load_transfers()
        if stock_cache is None:
            stock_cache = {}
            
        combined_data = self._get_combined_data(branch, all_transfers, stock_cache)
        if not combined_data:
            return 0, 0
            
        merged_payload, separate_payload = self._prepare_payloads(combined_data, branch)
        
        if merged_payload or separate_payload:
            self._repository.save_combined_transfers(
                branch=branch,
                merged_data=merged_payload,
                separate_data=separate_payload,
                timestamp=self._timestamp
            )
            return len(merged_payload), len(separate_payload)
            
        return 0, 0

    def _get_combined_data(self, branch: Branch, all_transfers: List[Transfer], stock_cache: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Combines normal transfers and surplus for a branch."""
        # Normal transfers for this sender
        branch_transfers = [t for t in all_transfers if t.from_branch.name == branch.name]
        
        # Branch balances for sender
        if branch.name not in stock_cache:
            stock_cache[branch.name] = self._repository.load_stock_levels(branch)
        sender_stock = stock_cache[branch.name]
        
        records = []
        for t in branch_transfers:
            # Get receiver balances (from cache or disk)
            if t.to_branch.name not in stock_cache:
                stock_cache[t.to_branch.name] = self._repository.load_stock_levels(t.to_branch)
            target_stock = stock_cache[t.to_branch.name]
            
            records.append({
                'code': t.product.code,
                'product_name': t.product.name,
                'quantity_to_transfer': t.quantity,
                'target_branch': t.to_branch.name,
                'transfer_type': 'normal',
                'sender_balance': sender_stock.get(t.product.code).balance if t.product.code in sender_stock else 0,
                'receiver_balance': target_stock.get(t.product.code).balance if t.product.code in target_stock else 0
            })
            
        # Remaining surplus
        surplus = self._repository.load_remaining_surplus(branch)
        
        # Admin stock
        if 'admin' not in stock_cache:
            stock_cache['admin'] = self._repository.load_stock_levels(Branch(name='admin'))
        admin_stock = stock_cache['admin']
        
        for s in surplus:
            records.append({
                'code': s['code'],
                'product_name': s['product_name'],
                'quantity_to_transfer': s['quantity'],
                'target_branch': 'admin',
                'transfer_type': 'surplus',
                'sender_balance': sender_stock.get(s['code']).balance if s['code'] in sender_stock else 0,
                'receiver_balance': admin_stock.get(s['code']).balance if s['code'] in admin_stock else 0
            })
            
        return records

    def _prepare_payloads(self, records: List[Dict], branch: Branch):
        """Groups records by category and target for saving."""
        df = pd.DataFrame(records)
        df['product_type'] = df['product_name'].apply(classify_product_type)
        
        # Merged (per category)
        merged = []
        for cat in df['product_type'].unique():
            cat_df = df[df['product_type'] == cat].copy()
            merged.append({
                'category': cat,
                'df': self._sort_df(cat_df)
            })
            
        # Separate (per target per category)
        separate = []
        for target in df['target_branch'].unique():
            target_df = df[df['target_branch'] == target]
            for cat in target_df['product_type'].unique():
                cat_df = target_df[target_df['product_type'] == cat].copy()
                separate.append({
                    'target': target,
                    'category': cat,
                    'df': self._sort_df(cat_df)
                })
                
        return merged, separate

    def _sort_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sorts and cleans up columns."""
        cols = [
            'code', 'product_name', 'quantity_to_transfer', 
            'target_branch', 'transfer_type', 
            'sender_balance', 'receiver_balance'
        ]
        # Keep only existing columns
        cols = [c for c in cols if c in df.columns]
        return df[cols].sort_values('product_name', key=lambda x: x.str.lower())

"""Domain service for combining transfers and surplus inventory."""

from typing import List, Dict, Tuple, Any
from src.domain.models.entities import Branch
from src.domain.models.distribution import Transfer
from src.core.domain.classification.product_classifier import classify_product_type


class ConsolidationEngine:
    """Handles the logical combination of transfers and surplus stock."""

    def combine_data(
        self,
        branch: Branch,
        transfers: List[Transfer],
        surplus_items: List[Dict],
        branch_balances: Dict[str, Dict[str, float]]
    ) -> Tuple[List[Dict], List[Dict]]:
        """Combines normal transfers and surplus for a branch."""
        records = []
        self._append_normal_transfers(records, branch, transfers, branch_balances)
        self._append_surplus_records(records, branch, surplus_items, branch_balances)
        
        if not records:
            return [], []
            
        return self._prepare_payloads(records)

    def _append_normal_transfers(self, records, branch, transfers, balances) -> None:
        """Processes normal transfers and adds them to the record list."""
        for transfer in transfers:
            sender_bal = balances.get(branch.name, {}).get(transfer.product.code, 0.0)
            target_bal = balances.get(transfer.to_branch.name, {}).get(transfer.product.code, 0.0)
            
            records.append({
                'code': transfer.product.code,
                'product_name': transfer.product.name,
                'quantity_to_transfer': transfer.quantity,
                'target_branch': transfer.to_branch.name,
                'transfer_type': 'normal',
                'sender_balance': sender_bal, 'receiver_balance': target_bal
            })

    def _append_surplus_records(self, records, branch, surplus_items, balances) -> None:
        """Processes surplus items (targeted at admin) and adds them to records."""
        admin_balances = balances.get('admin', {})
        for surplus in surplus_items:
            sender_bal = balances.get(branch.name, {}).get(surplus['code'], 0.0)
            target_bal = admin_balances.get(surplus['code'], 0.0)
            
            records.append({
                'code': surplus['code'],
                'product_name': surplus['product_name'],
                'quantity_to_transfer': surplus['quantity'],
                'target_branch': 'admin',
                'transfer_type': 'surplus',
                'sender_balance': sender_bal, 'receiver_balance': target_bal
            })

    def _prepare_payloads(self, records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Groups records by category and target for saving."""
        import pandas as pd
        df = pd.DataFrame(records)
        df['product_category'] = df['product_name'].apply(classify_product_type)
        
        merged = self._create_merged_payloads(df)
        separate = self._create_separate_payloads(df)
        
        return merged, separate

    def _create_merged_payloads(self, df) -> List[Dict]:
        """Creates category-grouped payloads."""
        payloads = []
        for category in df['product_category'].unique():
            category_df = df[df['product_category'] == category].copy()
            payloads.append({
                'category': category,
                'df': self._standardize_df(category_df)
            })
        return payloads

    def _create_separate_payloads(self, df) -> List[Dict]:
        """Creates target-and-category-grouped payloads."""
        payloads = []
        for target in df['target_branch'].unique():
            target_df = df[df['target_branch'] == target]
            for category in target_df['product_category'].unique():
                category_df = target_df[target_df['product_category'] == category].copy()
                payloads.append({
                    'target': target, 'category': category,
                    'df': self._standardize_df(category_df)
                })
        return payloads

    def _standardize_df(self, dataframe) -> Any:
        """Standardizes columns and sorts by product name."""
        cols = [
            'code', 'product_name', 'quantity_to_transfer', 
            'target_branch', 'transfer_type', 
            'sender_balance', 'receiver_balance'
        ]
        existing = [c for c in cols if c in dataframe.columns]
        return dataframe[existing].sort_values(
            'product_name', key=lambda x: x.str.lower()
        )

"""Domain service for combining transfers and surplus inventory."""

from typing import List, Dict, Any, Tuple
from src.domain.models.entities import Branch
from src.domain.models.distribution import Transfer
from src.core.domain.classification.product_classifier import classify_product_type

class ConsolidationEngine:
    """
    Handles the logical combination of transfers and surplus stock.
    Assigns balances and groups data by category and target.
    """

    def combine_data(
        self,
        branch: Branch,
        transfers: List[Transfer],
        surplus_items: List[Dict[str, Any]],
        branch_balances: Dict[str, Dict[str, float]]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Combines normal transfers and surplus for a branch.
        Returns (merged_payload, separate_payload).
        """
        records = []
        
        # 1. Process Normal Transfers
        for transfer in transfers:
            sender_balance = branch_balances.get(branch.name, {}).get(transfer.product.code, 0.0)
            receiver_balance = branch_balances.get(transfer.to_branch.name, {}).get(transfer.product.code, 0.0)
            
            records.append({
                'code': transfer.product.code,
                'product_name': transfer.product.name,
                'quantity_to_transfer': transfer.quantity,
                'target_branch': transfer.to_branch.name,
                'transfer_type': 'normal',
                'sender_balance': sender_balance,
                'receiver_balance': receiver_balance
            })
            
        # 2. Process Remaining Surplus (Always targeted at admin)
        admin_balances = branch_balances.get('admin', {})
        for surplus in surplus_items:
            sender_balance = branch_balances.get(branch.name, {}).get(surplus['code'], 0.0)
            receiver_balance = admin_balances.get(surplus['code'], 0.0)
            
            records.append({
                'code': surplus['code'],
                'product_name': surplus['product_name'],
                'quantity_to_transfer': surplus['quantity'],
                'target_branch': 'admin',
                'transfer_type': 'surplus',
                'sender_balance': sender_balance,
                'receiver_balance': receiver_balance
            })
            
        if not records:
            return [], []
            
        return self._prepare_payloads(records)

    def _prepare_payloads(self, records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Groups records by category and target for saving."""
        import pandas as pd
        
        data_frame = pd.DataFrame(records)
        data_frame['product_category'] = data_frame['product_name'].apply(classify_product_type)
        
        # A. Merged Output (Grouped by Category)
        merged_payloads = []
        unique_categories = data_frame['product_category'].unique()
        
        for category in unique_categories:
            category_df = data_frame[data_frame['product_category'] == category].copy()
            merged_payloads.append({
                'category': category,
                'df': self._sort_and_filter_dataframe(category_df)
            })
            
        # B. Separate Output (Grouped by Target and Category)
        separate_payloads = []
        unique_targets = data_frame['target_branch'].unique()
        
        for target in unique_targets:
            target_df = data_frame[data_frame['target_branch'] == target]
            unique_target_categories = target_df['product_category'].unique()
            
            for category in unique_target_categories:
                category_df = target_df[target_df['product_category'] == category].copy()
                separate_payloads.append({
                    'target': target,
                    'category': category,
                    'df': self._sort_and_filter_dataframe(category_df)
                })
                
        return merged_payloads, separate_payloads

    def _sort_and_filter_dataframe(self, results_dataframe: Any) -> Any:
        """Standardizes columns and sorts by product name."""
        intended_columns = [
            'code', 'product_name', 'quantity_to_transfer', 
            'target_branch', 'transfer_type', 
            'sender_balance', 'receiver_balance'
        ]
        # Keep only existing columns
        existing_columns = [col for col in intended_columns if col in results_dataframe.columns]
        return results_dataframe[existing_columns].sort_values('product_name', key=lambda x: x.str.lower())

"""Presenter for transforming domain reports into dataframes."""

import pandas as pd
from typing import List, Dict
from src.domain.models.distribution import ConsolidatedLogisticsReport


class LogisticsPresenter:
    """Transforms domain entities into payloads for the repository."""

    def prepare_payloads(
        self, report: ConsolidatedLogisticsReport
    ) -> tuple[List[Dict], List[Dict]]:
        """Main entry point for generating merged and separate payloads."""
        if not report.has_records():
            return [], []

        dataframe = self._to_dataframe(report)
        merged_payloads = self._create_merged_payloads(dataframe)
        separate_payloads = self._create_separate_payloads(dataframe)
        
        return merged_payloads, separate_payloads

    def _to_dataframe(
        self, 
        report: ConsolidatedLogisticsReport
    ) -> pd.DataFrame:
        """Converts domain records into a single pandas DataFrame."""
        rows = []
        for record in report.records:
            rows.append({
                'code': record.product.code,
                'product_name': record.product.name,
                'quantity_to_transfer': record.quantity,
                'target_branch': record.target_branch,
                'transfer_type': record.transfer_type,
                'sender_balance': record.sender_balance,
                'receiver_balance': record.receiver_balance,
                'product_category': record.category or 'other'
            })
        return pd.DataFrame(rows)

    def _create_merged_payloads(self, df: pd.DataFrame) -> List[Dict]:
        """Creates category-grouped payloads."""
        payloads = []
        for category in df['product_category'].unique():
            category_df = df[df['product_category'] == category].copy()
            payloads.append({
                'category': category,
                'df': self._standardize_df(category_df)
            })
        return payloads

    def _create_separate_payloads(self, df: pd.DataFrame) -> List[Dict]:
        """Creates target-and-category-grouped payloads."""
        payloads = []
        for target in df['target_branch'].unique():
            target_df = df[df['target_branch'] == target]
            for category in target_df['product_category'].unique():
                category_df = target_df[
                    target_df['product_category'] == category
                ].copy()
                payloads.append({
                    'target': target, 'category': category,
                    'df': self._standardize_df(category_df)
                })
        return payloads

    def _standardize_df(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Standardizes columns and sorts by product name."""
        column_order = [
            'code', 'product_name', 'quantity_to_transfer', 
            'target_branch', 'transfer_type', 
            'sender_balance', 'receiver_balance'
        ]
        present_cols = [c for c in column_order if c in dataframe.columns]
        sorted_df = dataframe[present_cols].sort_values(
            'product_name', key=lambda x: x.str.lower()
        )
        return sorted_df

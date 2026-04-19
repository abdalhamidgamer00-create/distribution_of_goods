"""Centralized domain policy for inventory adjustments and business rules."""

import math
import pandas as pd
from src.shared.constants import (
    MAX_BALANCE_FOR_NEED_THRESHOLD,
    MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION,
    MIN_NEED_THRESHOLD
)


class InventoryPolicy:
    """
    Centralizes business rules for stock requirements.
    Provides vectorized implementations for consistency.
    """

    @staticmethod
    def apply_vectorized_rules(dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Applies stock adjustment rules to a pandas DataFrame (Vectorized).
        
        Args:
            dataframe: DataFrame containing 'balance', 'coverage_quantity', 'needed_quantity'
            
        Returns:
            pd.DataFrame: Modified DataFrame
        """
        df = dataframe.copy()
        
        # Rule 1: Max Balance Suppression
        df.loc[
            df['balance'] >= MAX_BALANCE_FOR_NEED_THRESHOLD, 
            'needed_quantity'
        ] = 0
        
        # Rule 2: Small Need Suppression
        small_need_mask = (
            (df['coverage_quantity'] >= MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION) &
            (df['needed_quantity'] > 0) & 
            (df['needed_quantity'] < MIN_NEED_THRESHOLD)
        )
        df.loc[small_need_mask, 'needed_quantity'] = 0
        
        # Rule 3: Max Balance Capping
        available_space = (MAX_BALANCE_FOR_NEED_THRESHOLD - df['balance']).clip(lower=0)
        df['needed_quantity'] = df['needed_quantity'].clip(upper=available_space)
        
        return df

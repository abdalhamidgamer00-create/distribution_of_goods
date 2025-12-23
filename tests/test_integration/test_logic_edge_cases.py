import pytest
import pandas as pd
import math
from unittest.mock import patch
from src.core.domain.calculations.quantity_calculator import calculate_basic_quantities

class TestQuantityCalculatorPrecision:
    def test_calculate_basic_quantities_rounding(self):
        """Test that needed quantity handles small decimals in a stable way via calculate_basic_quantities."""
        # avg_sales=1/30 (so monthly=1), balance=0.1 -> needed = 1 - 0.1 = 0.9 -> ceil(0.9) = 1
        df = pd.DataFrame({'avg_sales': [1.0/30.0], 'balance': [0.1]})
        result_df = calculate_basic_quantities(df)
        
        assert result_df.iloc[0]['monthly_quantity'] == 1
        assert result_df.iloc[0]['needed_quantity'] == 1 # ceil(1 - 0.1)
        
        # If balance > monthly
        df = pd.DataFrame({'avg_sales': [1.0/30.0], 'balance': [10.0]})
        result_df = calculate_basic_quantities(df)
        assert result_df.iloc[0]['needed_quantity'] == 0
        assert result_df.iloc[0]['surplus_quantity'] == 9 # floor(10 - 1)

class TestSplittingFacadEdgeCases:
    @patch('src.services.splitting.core.splitter.validate_csv_input')
    @patch('src.services.splitting.core.splitter.get_branches')
    @patch('src.services.splitting.core.splitter.execute_split')
    def test_split_csv_by_branches_facade(self, mock_execute, mock_branches, mock_validate):
        """Test the high-level splitting facade edge behavior."""
        from src.services.splitting.core.splitter import split_csv_by_branches
        mock_branches.return_value = ['branch1']
        mock_execute.return_value = ({'branch1': 'path1'}, {})
        
        result = split_csv_by_branches("dummy.csv", "out", "base")
        assert result[0] == {'branch1': 'path1'}
        mock_validate.assert_called_once()

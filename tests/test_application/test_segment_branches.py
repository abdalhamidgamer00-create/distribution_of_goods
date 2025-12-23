"""Tests for the SegmentBranches use case."""

import pytest
from unittest.mock import MagicMock
from src.application.use_cases.segment_branches import SegmentBranches
from src.domain.services.branch_service import BranchSplitter
from src.domain.models.entities import (
    Branch, Product, StockLevel, ConsolidatedStock
)


class TestSegmentBranches:
    
    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.load_branches.return_value = [
            Branch(name="branch_a"), 
            Branch(name="branch_b")
        ]
        
        product = Product(code="P1", name="Product 1")
        stock_a = StockLevel(needed=10, surplus=0, balance=5.0, avg_sales=1.0)
        stock_b = StockLevel(needed=0, surplus=20, balance=50.0, avg_sales=1.0)
        
        repo.load_consolidated_stock.return_value = [
            ConsolidatedStock(
                product=product, 
                branch_stocks={"branch_a": stock_a, "branch_b": stock_b}
            )
        ]
        return repo

    @pytest.fixture
    def splitter(self):
        return BranchSplitter()

    def test_execute_calls_repository_methods(self, mock_repo, splitter):
        # Arrange
        use_case = SegmentBranches(mock_repo, splitter)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result is True
        mock_repo.load_branches.assert_called_once()
        mock_repo.load_consolidated_stock.assert_called_once()
        assert mock_repo.save_branch_stocks.call_count == 2
        
    def test_execute_saves_correct_data_per_branch(self, mock_repo, splitter):
        # Arrange
        use_case = SegmentBranches(mock_repo, splitter)
        
        # Act
        use_case.execute()
        
        # Verify branch A save call
        branch_a_call = mock_repo.save_branch_stocks.call_args_list[0]
        branch_a = branch_a_call[0][0]
        stocks_a = branch_a_call[0][1]
        
        assert branch_a.name == "branch_a"
        assert len(stocks_a) == 1
        assert stocks_a[0].stock.needed == 10
        
        # Verify branch B save call
        branch_b_call = mock_repo.save_branch_stocks.call_args_list[1]
        branch_b = branch_b_call[0][0]
        stocks_b = branch_b_call[0][1]
        
        assert branch_b.name == "branch_b"
        assert len(stocks_b) == 1
        assert stocks_b[0].stock.surplus == 20

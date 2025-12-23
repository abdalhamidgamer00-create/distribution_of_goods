"""Refactored Handler for Step 7: Generate Transfers."""

import os
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.domain.services.distribution_service import DistributionEngine
from src.domain.services.priority_service import PriorityCalculator
from src.application.use_cases.process_distributions import ProcessDistributions

def step_7_generate_transfers(use_latest_file: bool = None, **kwargs) -> bool:
    """
    Orchestrates Step 7 using Clean Architecture components.
    """
    # Source: branches/analytics (output of Step 6)
    # Target: transfers/csv
    stock_dir = os.path.join("data", "output", "branches", "analytics")
    transfer_dir = os.path.join("data", "output", "transfers", "csv")
    renamed_dir = os.path.join("data", "output", "converted", "renamed")
    
    if not os.path.exists(stock_dir):
        print(f"Error: stock directory {stock_dir} not found.")
        return False

    class UnifiedRepository(PandasDataRepository):
        def __init__(self, stock_dir, transfer_dir, renamed_dir):
            super().__init__(input_dir=renamed_dir, output_dir=stock_dir)
            self._transfer_dir = transfer_dir
            
        def save_transfers(self, transfers):
            old_output = self._output_dir
            self._output_dir = self._transfer_dir
            super().save_transfers(transfers)
            self._output_dir = old_output

    repository = UnifiedRepository(
        stock_dir=stock_dir,
        transfer_dir=transfer_dir,
        renamed_dir=renamed_dir
    )
    
    try:
        # Check if we have products to distribute
        products = repository.load_products()
        if not products:
            print("Error: No products found for distribution.")
            return False
            
        priority_calculator = PriorityCalculator()
        engine = DistributionEngine(priority_calculator)
        use_case = ProcessDistributions(repository, engine)
        
        use_case.execute()
        return True
    except Exception as e:
        print(f"Error in Step 7: {e}")
        import traceback
        traceback.print_exc()
        return False

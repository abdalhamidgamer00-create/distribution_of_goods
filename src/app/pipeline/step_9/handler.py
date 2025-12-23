"""Refactored Handler for Step 9: Remaining Surplus."""

import os
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.domain.services.distribution_service import DistributionEngine
from src.domain.services.priority_service import PriorityCalculator
from src.application.use_cases.process_distributions import ProcessDistributions

def step_9_generate_remaining_surplus(
    use_latest_file: bool = None, **kwargs
) -> bool:
    """
    Orchestrates Step 9 using Clean Architecture components.
    """
    stock_dir = "data/output/branches/analytics"
    surplus_dir = "data/output/remaining_surplus"
    renamed_dir = "data/output/converted/renamed"
    
    if not os.path.exists(stock_dir):
        return False

    # Use the enhanced repository directly with surplus_dir explicitly set
    repository = PandasDataRepository(
        input_dir=renamed_dir,
        output_dir=stock_dir,
        surplus_dir=surplus_dir
    )
    
    try:
        priority_calculator = PriorityCalculator()
        engine = DistributionEngine(priority_calculator)
        use_case = ProcessDistributions(repository, engine)
        
        results = use_case.calculate()
        repository.save_remaining_surplus(results)
        return True
    except Exception as e:
        print(f"Error in Step 9: {e}")
        return False

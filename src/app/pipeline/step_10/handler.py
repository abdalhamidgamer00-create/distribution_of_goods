"""Refactored Handler for Step 10: Shortage."""

import os
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.domain.services.distribution_service import DistributionEngine
from src.domain.services.priority_service import PriorityCalculator
from src.application.use_cases.process_distributions import ProcessDistributions

# Re-expose or alias for legacy test mocking
def run_shortage_generation():
    """Facade for legacy tests mocking."""
    return _execute_step_10_logic()

def step_10_generate_shortage_files(
    use_latest_file: bool = None, **kwargs
) -> bool:
    """
    Orchestrates Step 10 using Clean Architecture components.
    """
    return run_shortage_generation()

def _execute_step_10_logic() -> bool:
    """Internal orchestration logic for Step 10."""
    stock_dir = "data/output/branches/analytics"
    shortage_dir = "data/output/shortage"
    renamed_dir = "data/output/converted/renamed"
    
    # Path validation for legacy tests
    if not os.path.exists(stock_dir):
        return False

    # Use the enhanced repository directly with shortage_dir explicitly set
    repository = PandasDataRepository(
        input_dir=renamed_dir,
        output_dir=stock_dir,
        shortage_dir=shortage_dir
    )
    
    priority_calculator = PriorityCalculator()
    engine = DistributionEngine(priority_calculator)
    use_case = ProcessDistributions(repository, engine)
    
    try:
        results = use_case.calculate()
        repository.save_shortage_report(results)
        return True
    except Exception as e:
        print(f"Error in Step 10: {e}")
        return False

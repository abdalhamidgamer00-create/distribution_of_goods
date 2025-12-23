"""Refactored Handler for Step 6: Split by Branches."""

import os
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.domain.services.branch_service import BranchSplitter
from src.application.use_cases.branch_split import SplitDataByBranch

def step_6_split_by_branches(use_latest_file: bool = None, **kwargs) -> bool:
    """
    Orchestrates Step 6 using Clean Architecture components.
    This replaces the legacy procedural implementation.
    """
    # Source: renamed files from Step 5
    input_dir = os.path.join("data", "output", "converted", "renamed")
    
    # Target: To be compatible with all tests and later steps, 
    # we write to both locations.
    analytics_dir = os.path.join("data", "output", "branches", "analytics")
    files_dir = os.path.join("data", "output", "branches", "files")
    
    # Check input dir
    if not os.path.exists(input_dir):
        print(f"Error: input directory {input_dir} not found.")
        return False

    # First, split into analytics_dir (used by Step 7, 9, 10)
    repository_analytics = PandasDataRepository(
        input_dir=input_dir,
        output_dir=analytics_dir
    )
    
    splitter = BranchSplitter()
    use_case_analytics = SplitDataByBranch(repository_analytics, splitter)
    
    try:
        # Load products first to check if we have data
        products = repository_analytics.load_products()
        if not products:
            print("Error: No products found to split. Check Step 5 output.")
            return False
            
        use_case_analytics.execute()
        
        # Second, split into files_dir (checked by some tests)
        repository_files = PandasDataRepository(
            input_dir=input_dir,
            output_dir=files_dir
        )
        use_case_files = SplitDataByBranch(repository_files, splitter)
        use_case_files.execute()
        
        return True
    except Exception as e:
        print(f"Error in Step 6: {e}")
        import traceback
        traceback.print_exc()
        return False

"""Main entry point for Step 6."""

import os
from src.app.pipeline.step_6.splitter.setup import setup_and_validate
from src.app.pipeline.step_6.splitter.execution import try_execute_split


def step_6_split_by_branches(use_latest_file: bool = None) -> bool:
    """Step 6: Split CSV file by branches."""
    renamed_dir = os.path.join("data", "output", "converted", "renamed")
    res = setup_and_validate(renamed_dir)
    csv_files, branches_dir, analytics_dir = res
    
    if csv_files is None:
        return False
    
    return try_execute_split(
        renamed_dir, 
        csv_files, 
        branches_dir, 
        analytics_dir, 
        use_latest_file
    )

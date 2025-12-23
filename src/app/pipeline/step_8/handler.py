"""Refactored Handler for Step 8: Split Transfer Files by Product Type."""

import os
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.application.use_cases.split_transfers import SplitTransfersByCategory

def step_8_split_by_product_type(use_latest_file: bool = None, **kwargs) -> bool:
    """
    Step 8: Split transfer files into 6 categories and convert them to Excel.
    """
    # Source/CSV Target: data/output/transfers/csv
    # Excel Target: data/output/transfers/excel
    transfers_csv_dir = os.path.join("data", "output", "transfers", "csv")
    transfers_excel_dir = os.path.join("data", "output", "transfers", "excel")
    
    # Check if input directory exists
    if not os.path.exists(transfers_csv_dir):
        print(f"Error: Transfers CSV directory {transfers_csv_dir} does not exist.")
        return False
        
    repository = PandasDataRepository(
        input_dir="", # Not used for this step's load_transfers which uses output_dir
        output_dir=transfers_csv_dir
    )
    
    use_case = SplitTransfersByCategory(
        repository=repository,
        excel_output_dir=transfers_excel_dir
    )
    
    try:
        return use_case.execute()
    except Exception as e:
        print(f"Error in Step 8: {e}")
        import traceback
        traceback.print_exc()
        return False

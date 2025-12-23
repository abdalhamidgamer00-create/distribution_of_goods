import os
import shutil
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import all steps
from src.app.pipeline.step_1 import step_1_archive_output
from src.app.pipeline.step_2 import step_2_convert_excel_to_csv
from src.app.pipeline.step_3 import step_3_validate_data
from src.app.pipeline.step_4 import step_4_sales_analysis
from src.app.pipeline.step_5 import step_5_rename_columns
from src.app.pipeline.step_6 import step_6_split_by_branches
from src.app.pipeline.step_7 import step_7_generate_transfers
from src.app.pipeline.step_8 import step_8_split_by_product_type
from src.app.pipeline.step_9 import step_9_generate_remaining_surplus
from src.app.pipeline.step_10 import step_10_generate_shortage_files
from src.app.pipeline.step_11 import step_11_generate_combined_transfers

@pytest.fixture
def e2e_data_redirect():
    """Temporarily swap the real data directory for an E2E test directory."""
    root = Path.cwd()
    data_dir = root / "data"
    backup_dir = root / "data_real_backup"
    
    # 1. Backup real data if exists
    if data_dir.exists():
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        os.rename(data_dir, backup_dir)
    
    # 2. Create fresh data structure
    data_dir.mkdir()
    input_dir = data_dir / "input"
    input_dir.mkdir()
    
    # Create sample Excel file with ARABIC headers
    # Data designed to trigger: asherin(surplus) -> wardani(shortage)
    data = {
        "كود": ['001', '002', '003'],
        "إسم الصنف": ['PROD1', 'PROD2', 'PROD3'],
        "سعر البيع": [10, 20, 30],
        "الشركة": ['CO1', 'CO2', 'CO3'],
        "الوحدة": ['BOX', 'PC', 'BOX'],
        "إجمالى المبيعات": [1000, 1000, 1000],
        "إجمالى رصيد الصنف": [1000, 1000, 1000],
        "مبيعات العشرين": [0, 0, 0],
        "رصيد العشرين": [500, 500, 500],
        "مبيعات الوردانى": [500, 500, 500],
        "رصيد الوردانى": [0, 0, 0],
        "مبيعات العقبى": [10, 10, 10],
        "رصيد العقبى": [10, 10, 10],
        "مبيعات الشهيد": [10, 10, 10],
        "رصيد الشهيد": [10, 10, 10],
        "مبيعات النجوم": [10, 10, 10],
        "رصيد النجوم": [10, 10, 10],
        "مبيعات الادارة": [10, 10, 10],
        "رصيد الادارة": [10, 10, 10]
    }
    df = pd.DataFrame(data)
    df.to_excel(input_dir / "input_data.xlsx", index=False)
    
    yield data_dir
    
    # 3. Teardown
    if data_dir.exists():
        shutil.rmtree(data_dir)
    if backup_dir.exists():
        os.rename(backup_dir, data_dir)

def test_pipeline_full_execution(e2e_data_redirect):
    """Run all 11 steps in real 'data/' directory (swapped) and verify output."""
    
    steps = [
        ("Step 1", step_1_archive_output),
        ("Step 2", step_2_convert_excel_to_csv),
        ("Step 3", step_3_validate_data),
        ("Step 4", step_4_sales_analysis),
        ("Step 5", step_5_rename_columns),
        ("Step 6", step_6_split_by_branches),
        ("Step 7", step_7_generate_transfers),
        ("Step 8", step_8_split_by_product_type),
        ("Step 9", step_9_generate_remaining_surplus),
        ("Step 10", step_10_generate_shortage_files),
        ("Step 11", step_11_generate_combined_transfers)
    ]

    with patch('src.app.pipeline.utils.file_selector.select_excel_file', return_value="input_data.xlsx"), \
         patch('src.app.pipeline.utils.file_selector.select_csv_file', return_value="input_data.csv"), \
         patch('src.app.pipeline.step_3.validator.validation.validate_csv_header', return_value=(True, None, None, "Valid")), \
         patch('src.app.pipeline.step_3.validator.validation.validate_csv_headers', return_value=(True, [], "Headers Valid")), \
         patch('src.app.pipeline.step_3.validator.modification.remove_first_row', return_value=True): 
        
        for name, func in steps:
            print(f"Executing {name}...")
            result = func(use_latest_file=True)
            assert result is True, f"{name} failed"

    # Final Verification
    output_base = e2e_data_redirect / "output"
    combined_dir = output_base / "combined_transfers"
    assert combined_dir.exists()
    
    # Use recursive glob to find Excel files in subdirectories
    merged_excel = list((combined_dir / "merged" / "excel").glob("**/*.xlsx"))
    assert len(merged_excel) > 0, "No merged Excel files found in combined_transfers/merged/excel"
    
    separate_excel = list((combined_dir / "separate" / "excel").glob("**/*.xlsx"))
    assert len(separate_excel) > 0, "No separate Excel files found in combined_transfers/separate/excel"
    
    print(f"E2E Test Success! Found {len(merged_excel)} merged and {len(separate_excel)} separate Excel files.")

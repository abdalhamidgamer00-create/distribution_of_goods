"""End-to-end integration tests for the distribution pipeline."""

import os
import shutil
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch
from src.app.core.workflow import PipelineManager


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
    """Run all steps using PipelineManager in the test data directory and verify output."""
    
    manager = PipelineManager()

    # We patch the interactive file selection to return our test file
    with patch('src.infrastructure.services.file_selector.FileSelectorService.select_excel_file', return_value="input_data.xlsx"), \
         patch('src.infrastructure.services.file_selector.FileSelectorService.select_csv_file', return_value="input_data.csv"), \
         patch('src.application.use_cases.validate_inventory.validate_csv_header', return_value=(True, "2023-01-01", "2023-03-31", "Valid")), \
         patch('src.application.use_cases.validate_inventory.validate_csv_headers', return_value=(True, [], "Headers Valid")):
        
        # Run all steps sequentially or using run_all
        result = manager.run_all(use_latest_file=True)
        assert result is True, "Pipeline failed"

    # Final Verification of Output Structure
    output_base = e2e_data_redirect / "output"
    
    # 1. Converted directory
    assert (output_base / "converted" / "csv").exists()
    assert (output_base / "converted" / "renamed").exists()
    
    # 2. Branches directory
    assert (output_base / "branches" / "analytics").exists()
    
    # 3. Transfers directory
    assert (output_base / "transfers" / "csv").exists()
    
    # 4. Surplus directory
    assert (output_base / "remaining_surplus").exists()
    
    # 5. Combined Transfers directory
    combined_dir = output_base / "combined_transfers"
    assert combined_dir.exists()
    
    # Use recursive glob to find Excel files in subdirectories
    merged_excel = list((combined_dir / "merged" / "excel").glob("**/*.xlsx"))
    assert len(merged_excel) > 0, "No merged Excel files found in combined_transfers/merged/excel"
    
    separate_excel = list((combined_dir / "separate" / "excel").glob("**/*.xlsx"))
    assert len(separate_excel) > 0, "No separate Excel files found in combined_transfers/separate/excel"
    
    print(f"E2E Test Success! Found {len(merged_excel)} merged and {len(separate_excel)} separate Excel files.")

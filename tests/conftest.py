"""Pytest configuration and shared fixtures"""

import os
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_branch_df():
    """Create a sample branch DataFrame for testing"""
    return pd.DataFrame({
        'code': ['001', '002', '003', '004', '005'],
        'product_name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'selling_price': [10.0, 20.0, 15.0, 25.0, 30.0],
        'company': ['Company X', 'Company Y', 'Company X', 'Company Z', 'Company Y'],
        'unit': ['Box', 'Piece', 'Box', 'Piece', 'Box'],
        'total_sales': [100, 200, 150, 250, 300],
        'total_product_balance': [50, 100, 75, 125, 150],
        'sales': [20.0, 40.0, 30.0, 50.0, 60.0],
        'avg_sales': [0.5, 1.0, 0.75, 1.25, 1.5],
        'balance': [10.0, 20.0, 15.0, 5.0, 50.0]
    })


@pytest.fixture
def sample_branch_data(sample_branch_df):
    """Create sample branch data dictionary for testing"""
    from src.domain.services.branches.config import get_branches
    
    branches = get_branches()
    branch_data = {}
    
    for i, branch in enumerate(branches):
        df = sample_branch_df.copy()
        # Vary data slightly for each branch
        df['sales'] = df['sales'] * (1 + i * 0.1)
        df['avg_sales'] = df['avg_sales'] * (1 + i * 0.1)
        df['balance'] = df['balance'] * (1 + i * 0.05)
        
        # Calculate quantities
        from src.domain.services.calculations.quantity_calculator import calculate_basic_quantities
        df = calculate_basic_quantities(df)
        branch_data[branch] = df
    
    return branch_data


@pytest.fixture
def temp_directory():
    """Create a temporary directory for file tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_csv_content():
    """Sample CSV content with date header"""
    return """من: 01/09/2024 00:00 إلى: 01/12/2024 00:00
code,product_name,selling_price,company,unit,total_sales,total_product_balance,asherin_sales,asherin_balance,wardani_sales,wardani_balance,akba_sales,akba_balance,shahid_sales,shahid_balance,nujum_sales,nujum_balance,admin_sales,admin_balance
001,Product A,10.0,Company X,Box,100,50,20,10,15,8,25,12,10,5,18,9,12,6
002,Product B,20.0,Company Y,Piece,200,100,40,20,30,16,50,24,20,10,36,18,24,12"""


@pytest.fixture
def sample_csv_file(temp_directory, sample_csv_content):
    """Create a sample CSV file for testing"""
    csv_path = os.path.join(temp_directory, 'test_data.csv')
    with open(csv_path, 'w', encoding='utf-8-sig') as f:
        f.write(sample_csv_content)
    return csv_path


@pytest.fixture
def sample_analysis():
    """Sample analysis dictionary for report testing"""
    return {
        'total_rows': 100,
        'total_columns': 10,
        'total_cells': 1000,
        'filled_cells': 950,
        'empty_cells': 50,
        'empty_cells_percentage': 5.0,
        'date_range': {
            'start': '01/09/2024',
            'end': '01/12/2024'
        }
    }

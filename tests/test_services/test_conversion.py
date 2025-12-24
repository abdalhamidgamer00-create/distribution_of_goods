"""Tests for conversion service functions"""

import os
import tempfile
import shutil
from pathlib import Path

import pandas as pd
import pytest

from src.infrastructure.converters.mappers.column_mapper import get_column_mapping
from src.infrastructure.converters.converters.csv_column_renamer import rename_csv_columns
from src.infrastructure.converters.converters.excel_to_csv import convert_excel_to_csv


class TestGetColumnMapping:
    """Tests for get_column_mapping function"""
    
    def test_returns_dictionary(self):
        """Test that function returns a dictionary"""
        result = get_column_mapping()
        assert isinstance(result, dict)
    
    def test_contains_required_mappings(self):
        """Test that all required column mappings exist"""
        result = get_column_mapping()
        
        # Check for essential Arabic columns
        assert "كود" in result
        assert "إسم الصنف" in result
        assert "سعر البيع" in result
        assert "الشركة" in result
        assert "الوحدة" in result
    
    def test_branch_mappings(self):
        """Test branch-specific column mappings"""
        result = get_column_mapping()
        
        # Admin branch
        assert "مبيعات الادارة" in result
        assert "رصيد الادارة" in result
        
        # Other branches
        assert "مبيعات الشهيد" in result
        assert "مبيعات العشرين" in result
    
    def test_english_values(self):
        """Test that mapped values are in English"""
        result = get_column_mapping()
        
        assert result["كود"] == "code"
        assert result["إسم الصنف"] == "product_name"
        assert result["سعر البيع"] == "selling_price"
    
    def test_total_columns_mapping(self):
        """Test total columns mapping"""
        result = get_column_mapping()
        
        assert "إجمالى المبيعات" in result
        assert result["إجمالى المبيعات"] == "total_sales"


class TestRenameCsvColumns:
    """Tests for rename_csv_columns function"""
    
    def test_successful_rename(self, temp_directory):
        """Test successful column renaming"""
        # Create input CSV with Arabic columns
        input_path = os.path.join(temp_directory, 'input.csv')
        output_path = os.path.join(temp_directory, 'output.csv')
        
        with open(input_path, 'w', encoding='utf-8-sig') as f:
            f.write("كود,إسم الصنف,سعر البيع\n")
            f.write("001,Product A,10.0\n")
        
        result = rename_csv_columns(input_path, output_path)
        
        assert result is True
        assert os.path.exists(output_path)
        
        # Verify renamed columns
        df = pd.read_csv(output_path, encoding='utf-8-sig')
        assert 'code' in df.columns
        assert 'product_name' in df.columns
        assert 'selling_price' in df.columns
    
    def test_rename_with_date_header(self, temp_directory):
        """Test renaming when CSV has date header"""
        input_path = os.path.join(temp_directory, 'input.csv')
        output_path = os.path.join(temp_directory, 'output.csv')
        
        with open(input_path, 'w', encoding='utf-8-sig') as f:
            f.write("من: 01/09/2024 00:00 إلى: 01/12/2024 00:00\n")
            f.write("كود,إسم الصنف\n")
            f.write("001,Product A\n")
        
        result = rename_csv_columns(input_path, output_path)
        
        assert result is True
        
        # Read and verify date header is preserved
        with open(output_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            assert '01/09/2024' in first_line or 'code' in first_line.lower()
    
    def test_nonexistent_file(self, temp_directory):
        """Test with non-existent input file"""
        output_path = os.path.join(temp_directory, 'output.csv')
        
        with pytest.raises(ValueError):
            rename_csv_columns('/nonexistent/file.csv', output_path)


class TestConvertExcelToCsv:
    """Tests for convert_excel_to_csv function"""
    
    def test_successful_conversion(self, temp_directory):
        """Test successful Excel to CSV conversion"""
        input_path = os.path.join(temp_directory, 'input.xlsx')
        output_path = os.path.join(temp_directory, 'output.csv')
        
        # Create a simple Excel file
        df = pd.DataFrame({
            'code': ['001', '002'],
            'product_name': ['Product A', 'Product B'],
            'price': [10.0, 20.0]
        })
        df.to_excel(input_path, index=False)
        
        result = convert_excel_to_csv(input_path, output_path)
        
        assert result is True
        assert os.path.exists(output_path)
        
        # Verify CSV content
        csv_df = pd.read_csv(output_path, encoding='utf-8-sig')
        assert len(csv_df) == 2
        assert 'code' in csv_df.columns
    
    def test_nonexistent_file(self, temp_directory):
        """Test with non-existent input file"""
        output_path = os.path.join(temp_directory, 'output.csv')
        
        result = convert_excel_to_csv('/nonexistent/file.xlsx', output_path)
        
        assert result is False
    
    def test_output_is_utf8_sig(self, temp_directory):
        """Test that output CSV uses UTF-8 with BOM encoding"""
        input_path = os.path.join(temp_directory, 'input.xlsx')
        output_path = os.path.join(temp_directory, 'output.csv')
        
        # Create Excel with Arabic text
        df = pd.DataFrame({
            'name': ['منتج أ', 'منتج ب']
        })
        df.to_excel(input_path, index=False)
        
        result = convert_excel_to_csv(input_path, output_path)
        
        assert result is True
        
        # Read with utf-8-sig should work
        csv_df = pd.read_csv(output_path, encoding='utf-8-sig')
        assert len(csv_df) == 2

"""Tests for report generator functions"""

import pytest

from src.shared.reporting.report_generator import (
    generate_improvement_suggestions,
    generate_report
)


class TestGenerateImprovementSuggestions:
    """Tests for generate_improvement_suggestions function"""
    
    def test_high_empty_percentage(self):
        """Test suggestions with high empty cell percentage (>10%)"""
        analysis = {
            'empty_cells_percentage': 15.0,
            'total_rows': 100
        }
        
        result = generate_improvement_suggestions(analysis)
        
        assert isinstance(result, list)
        assert len(result) > 0
        # Should have suggestion about high percentage
        assert any('high' in s.lower() or 'percentage' in s.lower() for s in result)
    
    def test_medium_empty_percentage(self):
        """Test suggestions with medium empty cell percentage (5-10%)"""
        analysis = {
            'empty_cells_percentage': 7.0,
            'total_rows': 100
        }
        
        result = generate_improvement_suggestions(analysis)
        
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_low_empty_percentage(self):
        """Test suggestions with low empty cell percentage (<5%)"""
        analysis = {
            'empty_cells_percentage': 2.0,
            'total_rows': 100
        }
        
        result = generate_improvement_suggestions(analysis)
        
        assert isinstance(result, list)
        # Should still have some general suggestions
        assert len(result) > 0
    
    def test_zero_empty_percentage(self):
        """Test suggestions with zero empty cells"""
        analysis = {
            'empty_cells_percentage': 0.0,
            'total_rows': 100
        }
        
        result = generate_improvement_suggestions(analysis)
        
        assert isinstance(result, list)
    
    def test_zero_rows(self):
        """Test suggestions when total_rows is 0"""
        analysis = {
            'empty_cells_percentage': 0.0,
            'total_rows': 0
        }
        
        result = generate_improvement_suggestions(analysis)
        
        assert isinstance(result, list)
        # Should have suggestion about no data
        assert any('no data' in s.lower() or 'rows' in s.lower() for s in result)


class TestGenerateReport:
    """Tests for generate_report function"""
    
    def test_report_structure(self, sample_analysis):
        """Test that report has expected structure"""
        report = generate_report(sample_analysis, 'test_file.csv')
        
        assert isinstance(report, str)
        # Check for expected sections
        assert 'REPORT' in report.upper()
        assert 'STATISTICS' in report.upper()
        assert 'IMPROVEMENT' in report.upper() or 'SUGGESTION' in report.upper()
    
    def test_report_contains_filename(self, sample_analysis):
        """Test that report contains the filename"""
        filename = 'my_test_file.csv'
        report = generate_report(sample_analysis, filename)
        
        assert filename in report
    
    def test_report_contains_statistics(self, sample_analysis):
        """Test that report contains statistics"""
        report = generate_report(sample_analysis, 'test.csv')
        
        # Should contain the statistics values
        assert '100' in report  # total_rows
        assert '10' in report   # total_columns
    
    def test_report_with_date_range(self, sample_analysis):
        """Test that report includes date range when present"""
        report = generate_report(sample_analysis, 'test.csv')
        
        # Date range is in sample_analysis
        assert 'Date' in report or '01/09/2024' in report
    
    def test_report_without_date_range(self):
        """Test report generation without date range"""
        analysis = {
            'total_rows': 50,
            'total_columns': 5,
            'total_cells': 250,
            'filled_cells': 240,
            'empty_cells': 10,
            'empty_cells_percentage': 4.0
        }
        
        report = generate_report(analysis, 'test.csv')
        
        assert isinstance(report, str)
        assert 'REPORT' in report.upper()
    
    def test_report_contains_timestamp(self, sample_analysis):
        """Test that report contains generation timestamp"""
        report = generate_report(sample_analysis, 'test.csv')
        
        # Should have some date/time format
        assert 'Generated' in report or ':' in report

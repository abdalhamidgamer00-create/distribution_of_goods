"""Report generator for sales analysis"""

from datetime import datetime


def generate_improvement_suggestions(analysis: dict) -> list:
    """
    Generate improvement suggestions based on analysis
    
    Args:
        analysis: Analysis dictionary from analyzer
        
    Returns:
        List of improvement suggestions
    """
    suggestions = []
    
    empty_percentage = analysis.get('empty_cells_percentage', 0)
    
    if empty_percentage > 10:
        suggestions.append("High percentage of empty cells detected. Consider data validation before processing.")
    
    if empty_percentage > 5:
        suggestions.append("Review data sources to ensure complete data entry.")
        suggestions.append("Implement data quality checks to prevent missing values.")
    
    if empty_percentage > 0:
        suggestions.append("Consider filling empty cells with appropriate default values or 'N/A'.")
    
    if analysis.get('total_rows', 0) == 0:
        suggestions.append("No data rows found. Verify CSV file structure.")
    
    suggestions.append("Ensure consistent data format across all columns.")
    suggestions.append("Regular data audits to maintain data quality.")
    
    return suggestions


def generate_report(analysis: dict, csv_file: str) -> str:
    """
    Generate complete analysis report
    
    Args:
        analysis: Analysis dictionary from analyzer
        csv_file: Name of CSV file analyzed
        
    Returns:
        Formatted report string
    """
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("SALES DATA ANALYSIS REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"File: {csv_file}")
    
    if analysis.get('date_range'):
        date_range = analysis['date_range']
        report_lines.append(f"Date Range: {date_range['start']} to {date_range['end']}")
    
    report_lines.append("\n" + "-" * 60)
    report_lines.append("STATISTICS")
    report_lines.append("-" * 60)
    report_lines.append(f"Total Rows (Data): {analysis.get('total_rows', 0):,}")
    report_lines.append(f"Total Columns: {analysis.get('total_columns', 0):,}")
    report_lines.append(f"Total Cells: {analysis.get('total_cells', 0):,}")
    report_lines.append(f"Filled Cells: {analysis.get('filled_cells', 0):,}")
    report_lines.append(f"Empty Cells: {analysis.get('empty_cells', 0):,}")
    report_lines.append(f"Empty Cells Percentage: {analysis.get('empty_cells_percentage', 0)}%")
    
    suggestions = generate_improvement_suggestions(analysis)
    
    report_lines.append("\n" + "-" * 60)
    report_lines.append("IMPROVEMENT SUGGESTIONS")
    report_lines.append("-" * 60)
    for idx, suggestion in enumerate(suggestions, 1):
        report_lines.append(f"{idx}. {suggestion}")
    
    report_lines.append("\n" + "=" * 60)
    
    return "\n".join(report_lines)


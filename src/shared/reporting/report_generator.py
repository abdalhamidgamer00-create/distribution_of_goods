"""Report generator for sales analysis"""

from datetime import datetime


def _get_empty_cell_suggestions(empty_percentage: float) -> list:
    """Get suggestions based on empty cell percentage."""
    suggestions = []
    if empty_percentage > 10:
        suggestions.append("High percentage of empty cells detected. Consider data validation before processing.")
    if empty_percentage > 5:
        suggestions.append("Review data sources to ensure complete data entry.")
        suggestions.append("Implement data quality checks to prevent missing values.")
    if empty_percentage > 0:
        suggestions.append("Consider filling empty cells with appropriate default values or 'N/A'.")
    return suggestions


def _get_base_suggestions(total_rows: int) -> list:
    """Get base suggestions for data quality."""
    suggestions = []
    if total_rows == 0:
        suggestions.append("No data rows found. Verify CSV file structure.")
    suggestions.append("Ensure consistent data format across all columns.")
    suggestions.append("Regular data audits to maintain data quality.")
    return suggestions


def generate_improvement_suggestions(analysis: dict) -> list:
    """Generate improvement suggestions based on analysis."""
    empty_percentage = analysis.get('empty_cells_percentage', 0)
    total_rows = analysis.get('total_rows', 0)
    
    suggestions = _get_empty_cell_suggestions(empty_percentage)
    suggestions.extend(_get_base_suggestions(total_rows))
    return suggestions


def _generate_header(csv_file: str, analysis: dict) -> list:
    """Generate report header section."""
    lines = [
        "=" * 60,
        "SALES DATA ANALYSIS REPORT",
        "=" * 60,
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"File: {csv_file}",
    ]
    if analysis.get('date_range'):
        date_range = analysis['date_range']
        lines.append(f"Date Range: {date_range['start']} to {date_range['end']}")
    return lines


def _generate_statistics(analysis: dict) -> list:
    """Generate statistics section."""
    return [
        "\n" + "-" * 60,
        "STATISTICS",
        "-" * 60,
        f"Total Rows (Data): {analysis.get('total_rows', 0):,}",
        f"Total Columns: {analysis.get('total_columns', 0):,}",
        f"Total Cells: {analysis.get('total_cells', 0):,}",
        f"Filled Cells: {analysis.get('filled_cells', 0):,}",
        f"Empty Cells: {analysis.get('empty_cells', 0):,}",
        f"Empty Cells Percentage: {analysis.get('empty_cells_percentage', 0)}%",
    ]


def _format_suggestions(suggestions: list) -> list:
    """Format suggestions section."""
    lines = ["\n" + "-" * 60, "IMPROVEMENT SUGGESTIONS", "-" * 60]
    lines.extend(f"{idx}. {s}" for idx, s in enumerate(suggestions, 1))
    lines.append("\n" + "=" * 60)
    return lines


def generate_report(analysis: dict, csv_file: str) -> str:
    """Generate complete analysis report."""
    report_lines = _generate_header(csv_file, analysis)
    report_lines.extend(_generate_statistics(analysis))
    suggestions = generate_improvement_suggestions(analysis)
    report_lines.extend(_format_suggestions(suggestions))
    return "\n".join(report_lines)


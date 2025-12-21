"""
Excel formatter for Step 11

Converts CSV files to Excel with conditional formatting for balance columns.
- Red shades: values close to 0 (low stock warning)
- Green shades: values far from 0 (healthy stock)
"""

import os
import pandas as pd
from typing import List, Dict
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def convert_to_excel_with_formatting(csv_files: List[Dict], excel_output_dir: str) -> List[str]:
    """
    Convert CSV files to Excel with conditional formatting.
    
    Args:
        csv_files: List of dicts with 'path' key for CSV file paths
        excel_output_dir: Output directory for Excel files
        
    Returns:
        List of generated Excel file paths
    """
    excel_files = []
    
    for file_info in csv_files:
        csv_path = file_info.get('path')
        
        if not csv_path or not os.path.exists(csv_path):
            continue
        
        try:
            excel_path = _convert_single_file(csv_path, excel_output_dir)
            if excel_path:
                excel_files.append(excel_path)
        except Exception as e:
            logger.warning(f"Error converting {csv_path}: {e}")
    
    return excel_files


def _convert_single_file(csv_path: str, excel_output_dir: str) -> str:
    """Convert a single CSV file to Excel with formatting."""
    # Read CSV
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    if df.empty:
        return None
    
    # Get the relative path structure from CSV
    # Merged:   .../csv/combined_transfers_from_shahid_xxx/filename.csv (1 level)
    # Separate: .../csv/transfers_from_shahid_xxx/to_admin/filename.csv (2 levels)
    
    csv_dir = os.path.dirname(csv_path)  # immediate parent
    parent_dir = os.path.dirname(csv_dir)  # grandparent
    
    folder_name = os.path.basename(csv_dir)
    grandparent_name = os.path.basename(parent_dir)
    
    # Check if this is a "to_xxx" folder (separate files) or a branch folder (merged files)
    if folder_name.startswith('to_'):
        # Separate: 2-level structure
        source_folder = grandparent_name  # e.g., transfers_from_shahid_xxx
        target_folder = folder_name       # e.g., to_admin
        output_subdir = os.path.join(excel_output_dir, source_folder, target_folder)
    else:
        # Merged: 1-level structure
        source_folder = folder_name  # e.g., combined_transfers_from_shahid_xxx
        output_subdir = os.path.join(excel_output_dir, source_folder)
    
    os.makedirs(output_subdir, exist_ok=True)
    
    # Generate Excel filename
    excel_filename = os.path.basename(csv_path).replace('.csv', '.xlsx')
    excel_path = os.path.join(output_subdir, excel_filename)
    
    # Save to Excel first
    df.to_excel(excel_path, index=False, engine='openpyxl')
    
    # Apply formatting
    _apply_conditional_formatting(excel_path, df)
    
    logger.debug(f"Generated Excel: {excel_filename}")
    return excel_path


def _style_header_row(ws) -> None:
    """Style the header row with blue background and white text."""
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')


def _find_balance_columns(df: pd.DataFrame) -> tuple:
    """Find indices of sender and receiver balance columns."""
    sender_col = None
    receiver_col = None
    
    for idx, col in enumerate(df.columns, 1):
        if col == 'sender_balance':
            sender_col = idx
        elif col == 'receiver_balance':
            receiver_col = idx
    
    return sender_col, receiver_col


def _create_color_rule() -> ColorScaleRule:
    """Create color scale rule: Red (0) -> Yellow (15) -> Green (30+)."""
    return ColorScaleRule(
        start_type='num', start_value=0, start_color='FF0000',
        mid_type='num', mid_value=15, mid_color='FFFF00',
        end_type='num', end_value=30, end_color='00FF00'
    )


def _apply_color_scale_to_column(ws, col_idx: int, last_row: int, color_rule) -> None:
    """Apply color scale formatting to a column."""
    col_letter = get_column_letter(col_idx)
    ws.conditional_formatting.add(f"{col_letter}2:{col_letter}{last_row}", color_rule)


def _adjust_column_widths(ws, df: pd.DataFrame) -> None:
    """Adjust column widths based on content type."""
    width_map = {
        'code': 12,
        'product_name': 40,
        'quantity': 15, 'sender_balance': 15, 'receiver_balance': 15,
        'target_branch': 15, 'transfer_type': 15
    }
    
    for idx, col in enumerate(df.columns, 1):
        col_letter = get_column_letter(idx)
        ws.column_dimensions[col_letter].width = width_map.get(col, 12)


def _add_borders(ws, last_row: int, num_cols: int) -> None:
    """Add thin borders to all cells."""
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    
    for row in ws.iter_rows(min_row=1, max_row=last_row, min_col=1, max_col=num_cols):
        for cell in row:
            cell.border = thin_border


def _apply_conditional_formatting(excel_path: str, df: pd.DataFrame) -> None:
    """Apply conditional formatting to balance columns."""
    wb = load_workbook(excel_path)
    ws = wb.active
    last_row = len(df) + 1
    
    _style_header_row(ws)
    
    sender_col, receiver_col = _find_balance_columns(df)
    color_rule = _create_color_rule()
    
    if sender_col:
        _apply_color_scale_to_column(ws, sender_col, last_row, color_rule)
    if receiver_col:
        _apply_color_scale_to_column(ws, receiver_col, last_row, color_rule)
    
    _adjust_column_widths(ws, df)
    _add_borders(ws, last_row, len(df.columns))
    
    ws.freeze_panes = 'A2'
    wb.save(excel_path)
    wb.close()


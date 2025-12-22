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


def _process_single_csv(file_info: dict, excel_output_dir: str) -> str:
    """Process a single CSV file and return Excel path or None."""
    csv_path = file_info.get('path')
    if not csv_path or not os.path.exists(csv_path):
        return None
    try:
        return _convert_single_file(csv_path, excel_output_dir)
    except Exception as e:
        logger.warning(f"Error converting {csv_path}: {e}")
        return None


def convert_to_excel_with_formatting(csv_files: List[Dict], excel_output_dir: str) -> List[str]:
    """Convert CSV files to Excel with conditional formatting."""
    return [path for path in (_process_single_csv(f, excel_output_dir) for f in csv_files) if path]


def _get_output_subdir(excel_output_dir: str, folder_name: str, grandparent_name: str) -> str:
    """Get output subdirectory based on folder structure."""
    if folder_name.startswith('to_'):
        return os.path.join(excel_output_dir, grandparent_name, folder_name)
    return os.path.join(excel_output_dir, folder_name)


def _determine_output_path(csv_path: str, excel_output_dir: str) -> str:
    """Determine the output path for Excel file based on CSV structure."""
    csv_dir = os.path.dirname(csv_path)
    parent_dir = os.path.dirname(csv_dir)
    
    output_subdir = _get_output_subdir(excel_output_dir, os.path.basename(csv_dir), os.path.basename(parent_dir))
    os.makedirs(output_subdir, exist_ok=True)
    
    return os.path.join(output_subdir, os.path.basename(csv_path).replace('.csv', '.xlsx'))


def _convert_single_file(csv_path: str, excel_output_dir: str) -> str:
    """Convert a single CSV file to Excel with formatting."""
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    if df.empty:
        return None
    excel_path = _determine_output_path(csv_path, excel_output_dir)
    df.to_excel(excel_path, index=False, engine='openpyxl')
    _apply_conditional_formatting(excel_path, df)
    logger.debug(f"Generated Excel: {os.path.basename(excel_path)}")
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
    sender_col, receiver_col = None, None
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
    width_map = {'code': 12, 'product_name': 40, 'quantity': 15, 'sender_balance': 15, 'receiver_balance': 15, 'target_branch': 15, 'transfer_type': 15}
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


def _apply_balance_formatting(ws, df: pd.DataFrame, last_row: int) -> None:
    """Apply color scale formatting to balance columns."""
    sender_col, receiver_col = _find_balance_columns(df)
    color_rule = _create_color_rule()
    
    if sender_col:
        _apply_color_scale_to_column(ws, sender_col, last_row, color_rule)
    if receiver_col:
        _apply_color_scale_to_column(ws, receiver_col, last_row, color_rule)


def _apply_conditional_formatting(excel_path: str, df: pd.DataFrame) -> None:
    """Apply conditional formatting to balance columns."""
    wb = load_workbook(excel_path)
    ws = wb.active
    last_row = len(df) + 1
    _style_header_row(ws)
    _apply_balance_formatting(ws, df, last_row)
    _adjust_column_widths(ws, df)
    _add_borders(ws, last_row, len(df.columns))
    ws.freeze_panes = 'A2'; wb.save(excel_path); wb.close()


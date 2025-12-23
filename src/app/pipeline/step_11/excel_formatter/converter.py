"""CSV to Excel converter logic."""

import os
import pandas as pd
from openpyxl import load_workbook
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_11.excel_formatter import styling, rules, paths

logger = get_logger(__name__)


def apply_conditional_formatting(
    excel_path: str, dataframe: pd.DataFrame
) -> None:
    """Apply conditional formatting and styling to Excel file."""
    workbook = load_workbook(excel_path)
    worksheet = workbook.active
    last_row = len(dataframe) + 1
    
    styling.style_header_row(worksheet)
    rules.apply_balance_formatting(worksheet, dataframe, last_row)
    styling.adjust_column_widths(worksheet, dataframe)
    styling.add_borders(worksheet, last_row, len(dataframe.columns))
    
    worksheet.freeze_panes = 'A2'
    workbook.save(excel_path)
    workbook.close()


def convert_single_file(csv_path: str, excel_output_dir: str) -> str:
    """Convert a single CSV file to Excel with formatting."""
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    if df.empty:
        return None
        
    excel_path = paths.determine_output_path(csv_path, excel_output_dir)
    df.to_excel(excel_path, index=False, engine='openpyxl')
    
    apply_conditional_formatting(excel_path, df)
    logger.debug(f"Generated Excel: {os.path.basename(excel_path)}")
    return excel_path

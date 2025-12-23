"""Conditional formatting rules for Excel."""

from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter
import pandas as pd


def find_balance_columns(dataframe: pd.DataFrame) -> tuple:
    """Find indices of sender and receiver balance columns."""
    sender_column_index, receiver_column_index = None, None
    for column_index, column in enumerate(dataframe.columns, 1):
        if column == 'sender_balance':
            sender_column_index = column_index
        elif column == 'receiver_balance':
            receiver_column_index = column_index
    return sender_column_index, receiver_column_index


def create_color_rule() -> ColorScaleRule:
    """Create color scale rule: Red (0) -> Yellow (15) -> Green (30+)."""
    return ColorScaleRule(
        start_type='num', start_value=0, start_color='FF0000',
        mid_type='num', mid_value=15, mid_color='FFFF00',
        end_type='num', end_value=30, end_color='00FF00'
    )


def apply_color_scale_to_column(
    worksheet, column_index: int, last_row: int, color_rule
) -> None:
    """Apply color scale formatting to a column."""
    column_letter = get_column_letter(column_index)
    worksheet.conditional_formatting.add(
        f"{column_letter}2:{column_letter}{last_row}", color_rule
    )


def apply_balance_formatting(
    worksheet, dataframe: pd.DataFrame, last_row: int
) -> None:
    """Apply color scale formatting to balance columns."""
    sender_index, receiver_index = find_balance_columns(dataframe)
    color_rule = create_color_rule()
    
    if sender_index:
        apply_color_scale_to_column(
            worksheet, sender_index, last_row, color_rule
        )
    if receiver_index:
        apply_color_scale_to_column(
            worksheet, receiver_index, last_row, color_rule
        )

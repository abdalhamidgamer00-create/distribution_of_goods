"""Detail sections for the transfer ratio result view."""

import streamlit as st

from src.presentation.gui.utils.translations import BRANCH_NAMES
from src.presentation.gui.views.purchases.transfer_ratio_labels import (
    MISSING_LABELS,
    UNEXPECTED_LABELS,
)


def render_missing_items(result) -> None:
    """Render the missing-items section."""
    title = f"الأصناف غير المحولة ({len(result.missing)})"
    with st.expander(title, expanded=False):
        if result.missing.empty:
            st.success("لا توجد أصناف ناقصة.")
            return
        st.dataframe(
            display_frame(result.missing).rename(columns=MISSING_LABELS),
            width="stretch",
            hide_index=True,
        )


def render_unexpected_items(result) -> None:
    """Render the unexpected-items section."""
    title = (
        "أصناف موجودة في الملف النهائي وغير موجودة في المتوقع "
        f"({len(result.unexpected)})"
    )
    with st.expander(title, expanded=False):
        if result.unexpected.empty:
            st.info("لا توجد أصناف إضافية غير متوقعة.")
            return
        st.dataframe(
            display_frame(result.unexpected).rename(
                columns=UNEXPECTED_LABELS
            ),
            width="stretch",
            hide_index=True,
        )


def display_frame(dataframe):
    """Translate branch keys into display labels."""
    display = dataframe.copy()
    for column in ["source_branch", "target_branch"]:
        if column in display.columns:
            display[column] = display[column].map(format_branch)
    return display


def format_branch(branch_key: str) -> str:
    """Format a branch key for Arabic display."""
    if not branch_key or branch_key == "unassigned":
        return "غير محدد"
    return BRANCH_NAMES.get(branch_key, branch_key)

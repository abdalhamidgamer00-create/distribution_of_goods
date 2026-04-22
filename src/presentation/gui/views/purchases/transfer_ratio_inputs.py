"""Input and execution helpers for the transfer ratio page."""

import streamlit as st

from src.presentation.gui.services.transfer_ratio_service import (
    compare_transfer_workbook_sets,
)
from src.presentation.gui.views.purchases.transfer_ratio_labels import (
    PAGE_INFO,
    RESULT_KEY,
)


def render_upload_section():
    """Render upload controls and return uploaded files."""
    st.info(PAGE_INFO)
    left_column, right_column = st.columns(2)
    with left_column:
        expected_files = st.file_uploader(
            "الملفات المتوقعة للتحويل بين الفروع",
            type=["xlsx", "xls"],
            accept_multiple_files=True,
            key="expected_transfer_file",
        )
    with right_column:
        actual_files = st.file_uploader(
            "الملفات النهائية المحضرة",
            type=["xlsx", "xls"],
            accept_multiple_files=True,
            key="actual_transfer_file",
        )
    _render_file_counts(expected_files, actual_files)
    return expected_files, actual_files


def run_comparison(expected_files, actual_files) -> None:
    """Run workbook comparison when the user clicks the action button."""
    if not (expected_files and actual_files):
        return
    if not st.button("حساب نسبة التحويل", type="primary", width="stretch"):
        return
    try:
        with st.spinner("جاري تحليل الملفات وحساب النسبة..."):
            st.session_state[RESULT_KEY] = compare_transfer_workbook_sets(
                _uploaded_pairs(expected_files),
                _uploaded_pairs(actual_files),
            )
    except Exception as error:
        st.error(f"تعذر إتمام المقارنة: {error}")


def _render_file_counts(expected_files, actual_files) -> None:
    if expected_files:
        st.caption(
            f"عدد الملفات المتوقعة المرفوعة: {len(expected_files)}"
        )
    if actual_files:
        st.caption(
            f"عدد الملفات النهائية المرفوعة: {len(actual_files)}"
        )


def _uploaded_pairs(uploaded_files):
    return [
        (uploaded_file, uploaded_file.name)
        for uploaded_file in uploaded_files
    ]

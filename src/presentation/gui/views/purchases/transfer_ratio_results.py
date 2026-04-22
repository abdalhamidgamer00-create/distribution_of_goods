"""Result rendering helpers for the transfer ratio page."""

import streamlit as st

from src.presentation.gui.views.purchases.transfer_ratio_labels import (
    BRANCH_SUMMARY_LABELS,
    CODE_ONLY_INFO,
    RESULT_KEY,
)
from src.presentation.gui.views.purchases.transfer_ratio_result_details import (
    format_branch,
    render_missing_items,
    render_unexpected_items,
)


def render_comparison_result() -> None:
    """Render the latest comparison result from session state."""
    result = st.session_state.get(RESULT_KEY)
    if not result:
        return
    _render_summary_metrics(result.overall)
    st.caption(result.assumptions)
    _render_branch_summary(result)
    render_missing_items(result)
    render_unexpected_items(result)


def render_back_button() -> None:
    """Render the navigation button back to purchases."""
    st.markdown("---")
    if st.button("← العودة إلى قسم المشتريات", type="secondary"):
        st.switch_page("pages/purchasing_dashboard.py")


def _render_summary_metrics(overall: dict) -> None:
    summary_columns = st.columns(4)
    summary_columns[0].metric("الأصناف المتوقعة", overall["expected_items"])
    summary_columns[1].metric("الأصناف المطابقة", overall["matched_items"])
    summary_columns[2].metric("نسبة التحويل", f"{overall['item_ratio']:.2f}%")
    summary_columns[3].metric(
        "نسبة الكميات",
        f"{overall['quantity_ratio']:.2f}%",
    )
    _render_status_message(overall)


def _render_status_message(overall: dict) -> None:
    if overall["item_ratio"] >= 100:
        st.success(
            "النسبة 100%: كل الأصناف المتوقعة موجودة في الملف النهائي."
        )
        return
    st.warning(
        f"النسبة أقل من 100%: يوجد {overall['missing_items']} صنف/سطر "
        "متوقع لم يظهر في الملف النهائي."
    )


def _render_branch_summary(result) -> None:
    if not result.supports_branch_breakdown:
        st.info(CODE_ONLY_INFO)
        return
    st.markdown("### ملخص حسب الفرع المصدر")
    branch_summary = result.by_branch.copy()
    branch_summary["source_branch"] = branch_summary["source_branch"].map(
        format_branch
    )
    st.dataframe(
        branch_summary.rename(columns=BRANCH_SUMMARY_LABELS),
        width="stretch",
        hide_index=True,
    )

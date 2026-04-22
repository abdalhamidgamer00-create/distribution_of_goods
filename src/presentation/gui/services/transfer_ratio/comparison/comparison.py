"""Comparison entry points for transfer ratio workbooks."""

from __future__ import annotations

from src.presentation.gui.services.transfer_ratio.comparison.aggregation import (
    build_overall_summary,
    group_rows,
)
from src.presentation.gui.services.transfer_ratio.comparison.details import (
    build_assumptions,
    prepare_detail_frame,
    prepare_unexpected_frame,
)
from src.presentation.gui.services.transfer_ratio.comparison.loading import (
    load_workbooks,
)
from src.presentation.gui.services.transfer_ratio.comparison.merge import (
    branch_frame,
    matching_basis,
    merge_grouped,
    validate_rows,
)
from src.presentation.gui.services.transfer_ratio.shared.constants import (
    CODE_ONLY_MODE,
)
from src.presentation.gui.services.transfer_ratio.shared.models import (
    WorkbookComparison,
)


def compare_transfer_workbooks(
    expected_file,
    actual_file,
    expected_name=None,
    actual_name=None,
) -> WorkbookComparison:
    """Compare an expected workbook against the final workbook."""
    return compare_transfer_workbook_sets(
        [(expected_file, expected_name)],
        [(actual_file, actual_name)],
    )


def compare_transfer_workbook_sets(
    expected_files,
    actual_files,
) -> WorkbookComparison:
    """Compare multiple expected workbooks against final workbooks."""
    expected_rows = load_workbooks(expected_files, allow_code_only=False)
    actual_rows = load_workbooks(actual_files, allow_code_only=True)
    validate_rows(expected_rows, actual_rows)
    code_only_mode = actual_rows["comparison_mode"].eq(CODE_ONLY_MODE).all()
    expected_grouped = group_rows(expected_rows, code_only_mode=code_only_mode)
    actual_grouped = group_rows(actual_rows, code_only_mode=code_only_mode)
    merged = merge_grouped(expected_grouped, actual_grouped)
    return _comparison_result(
        merged,
        expected_grouped,
        actual_grouped,
        code_only_mode,
    )


def _comparison_result(
    merged,
    expected_grouped,
    actual_grouped,
    code_only_mode: bool,
) -> WorkbookComparison:
    missing = merged[merged["quantity_actual"] <= 0].copy()
    unexpected = actual_grouped[
        ~actual_grouped["comparison_key"].isin(
            expected_grouped["comparison_key"]
        )
    ].copy()
    return WorkbookComparison(
        overall=build_overall_summary(merged),
        by_branch=branch_frame(merged, code_only_mode),
        missing=prepare_detail_frame(missing, "expected"),
        unexpected=prepare_unexpected_frame(unexpected),
        expected_rows=expected_grouped,
        actual_rows=actual_grouped,
        assumptions=build_assumptions(code_only_mode),
        matching_basis=matching_basis(code_only_mode),
        supports_branch_breakdown=not code_only_mode,
    )

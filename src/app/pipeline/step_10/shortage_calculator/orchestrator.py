"""Orchestrator for shortage calculation."""

from src.core.domain.branches.config import get_branches
from src.app.pipeline.step_10.shortage_calculator import core, builder


def calculate_shortage_products(analytics_dir: str) -> tuple:
    """Calculate products where total needed exceeds total surplus."""
    branches = get_branches()
    product_totals, has_date_header, first_line = core.aggregate_branch_totals(
        analytics_dir, branches
    )
    shortage_dataframe = builder.build_shortage_dataframe(
        product_totals, branches
    )
    return shortage_dataframe, has_date_header, first_line

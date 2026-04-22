"""Key builders for transfer ratio comparison."""

from __future__ import annotations

from src.presentation.gui.services.transfer_ratio.shared.text_utils import (
    normalize_header,
)


def build_key(row, code_only_mode: bool = False) -> str:
    """Build a stable comparison key."""
    code = row.get("code", "") or row.get("product_name", "")
    if code_only_mode:
        return normalize_header(str(code))
    source = row.get("source_branch", "") or "unassigned"
    target = row.get("target_branch", "") or "unassigned"
    return f"{source}|{target}|{normalize_header(str(code))}"

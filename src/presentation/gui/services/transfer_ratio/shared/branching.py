"""Branch normalization and inference helpers."""

from __future__ import annotations

import os
import re

from src.presentation.gui.services.transfer_ratio.shared.constants import (
    BRANCH_PATTERNS,
)
from src.presentation.gui.services.transfer_ratio.shared.text_utils import (
    normalize_header,
)


def normalize_branch_name(value: object) -> str:
    """Normalize branch labels to canonical branch keys."""
    text = normalize_header(value)
    if not text:
        return ""
    for branch_key, aliases in BRANCH_PATTERNS.items():
        if text in _alias_tokens(aliases):
            return branch_key
    return text


def infer_branch_from_text(
    file_name: str,
    sheet_name: str,
    branch_role: str,
) -> str:
    """Infer source or target branch from the file or sheet name."""
    file_token = normalize_header(os.path.basename(file_name))
    sheet_token = normalize_header(sheet_name)
    for branch_key, aliases in BRANCH_PATTERNS.items():
        if _matches_role(file_token, aliases, branch_role):
            return branch_key
        if any(normalize_header(alias) == sheet_token for alias in aliases):
            return branch_key
    return ""


def _alias_tokens(aliases) -> set[str]:
    return {normalize_header(alias) for alias in aliases}


def _matches_role(file_token: str, aliases, branch_role: str) -> bool:
    patterns = _patterns_for_role(aliases, branch_role)
    return any(re.search(pattern, file_token) for pattern in patterns)


def _patterns_for_role(aliases, branch_role: str) -> list[str]:
    patterns = []
    for alias in aliases:
        token = normalize_header(alias)
        if branch_role == "source":
            patterns.extend(
                [
                    rf"from_{token}",
                    rf"{token}_combined",
                    rf"{token}_to_",
                    rf"_{token}_to_",
                ]
            )
        if branch_role == "target":
            patterns.extend(
                [
                    rf"to_{token}",
                    rf"target_{token}",
                    rf"_to_{token}_",
                ]
            )
    return patterns

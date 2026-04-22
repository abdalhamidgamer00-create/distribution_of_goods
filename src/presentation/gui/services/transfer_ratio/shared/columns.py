"""Column detection helpers for transfer ratio services."""

from __future__ import annotations

from typing import Iterable, Optional

from src.presentation.gui.services.transfer_ratio.shared.text_utils import (
    normalize_header,
)


def find_column(
    columns: Iterable[str],
    aliases: Iterable[str],
) -> Optional[str]:
    """Return the first matching column from a list of aliases."""
    normalized_aliases = {normalize_header(alias) for alias in aliases}
    for column in columns:
        if normalize_header(column) in normalized_aliases:
            return column
    return None

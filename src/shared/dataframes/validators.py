"""Shared dataframe validators and helpers."""

from __future__ import annotations

from typing import Iterable, Sequence

import pandas as pd


def ensure_columns(df: pd.DataFrame, required: Sequence[str], *, context: str = "") -> pd.DataFrame:
    """Validate that DataFrame contains the required columns."""
    missing = [col for col in required if col not in df.columns]
    if missing:
        ctx = f" for {context}" if context else ""
        raise ValueError(
            f"Missing required columns{ctx}: {', '.join(sorted(missing))}"
        )
    return df


def clean_numeric(value) -> float:
    """Coerce value into float, ignoring formatting characters."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().replace(",", ""))
        except ValueError:
            pass
    return 0.0


def clean_numeric_series(series: pd.Series) -> pd.Series:
    """Vectorized helper to coerce a series into floats."""
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0.0).astype(float)

    cleaned = series.astype(str).str.replace(",", "", regex=False)
    cleaned = cleaned.str.replace(r"[^0-9\-.]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)


def subset_rows(df: pd.DataFrame, mask: Iterable[bool]) -> pd.DataFrame:
    """Return a copy of df filtered by mask (as Series or iterable)."""
    return df.loc[mask].copy()

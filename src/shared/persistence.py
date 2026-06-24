"""Shared helpers for persisting DataFrames in dual CSV+Excel format."""

import os
from typing import Callable, Optional

import pandas as pd


def save_dual_format(
    dataframe: pd.DataFrame,
    csv_dir: str,
    excel_dir: str,
    filename_stem: str,
    excel_writer: Optional[Callable[[pd.DataFrame, str], None]] = None,
) -> None:
    """Save *dataframe* as both CSV and Excel under the given directories.

    This consolidates the recurring pattern of::

        os.makedirs(csv_dir, exist_ok=True)
        dataframe.to_csv(os.path.join(csv_dir, name + ".csv"), ...)
        os.makedirs(excel_dir, exist_ok=True)
        dataframe.to_excel(os.path.join(excel_dir, name + ".xlsx"), ...)

    Parameters
    ----------
    dataframe:
        The data to persist.
    csv_dir:
        Directory for the ``.csv`` output.
    excel_dir:
        Directory for the ``.xlsx`` output.
    filename_stem:
        Base filename **without** extension.
    excel_writer:
        Optional callable ``(df, path) -> None`` for custom Excel
        formatting (e.g. ``save_formatted_excel``).  When *None* the
        plain ``DataFrame.to_excel`` method is used.
    """
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, f"{filename_stem}.csv")
    dataframe.to_csv(csv_path, index=False, encoding="utf-8-sig")

    os.makedirs(excel_dir, exist_ok=True)
    excel_path = os.path.join(excel_dir, f"{filename_stem}.xlsx")
    if excel_writer is not None:
        excel_writer(dataframe, excel_path)
    else:
        dataframe.to_excel(excel_path, index=False)

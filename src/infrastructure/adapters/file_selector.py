"""Service for finding and selecting files in the filesystem."""

import os
from typing import List, Optional
from src.shared.utility.file_handler import get_excel_files, get_csv_files

class FileSelectorService:
    """Handles finding and selecting files based on various criteria."""

    @staticmethod
    def get_latest_excel(directory: str) -> Optional[str]:
        """Returns the most recently modified Excel file in the directory."""
        files = get_excel_files(directory)
        if not files:
            return None
        return max(
            files, key=lambda f: os.path.getmtime(
                os.path.join(directory, f)
            )
        )

    @staticmethod
    def get_latest_csv(directory: str) -> Optional[str]:
        """Returns the most recently modified CSV file in the directory."""
        files = get_csv_files(directory)
        if not files:
            return None
        return max(
            files, key=lambda f: os.path.getmtime(
                os.path.join(directory, f)
            )
        )

    @staticmethod
    def select_excel_file(directory: str, use_latest: bool = True) -> Optional[str]:
        """Selects an Excel file, either the latest or via user interaction."""
        if use_latest:
            return FileSelectorService.get_latest_excel(directory)
        return FileSelectorService.get_latest_excel(directory)

    @staticmethod
    def select_csv_file(directory: str, use_latest: bool = True) -> Optional[str]:
        """Selects a CSV file, either the latest or via user interaction."""
        if use_latest:
            return FileSelectorService.get_latest_csv(directory)
        return FileSelectorService.get_latest_csv(directory)

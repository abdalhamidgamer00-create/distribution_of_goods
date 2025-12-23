"""File generation helpers for Step 11."""

from src.app.pipeline.step_11.combiner import (
    generate_merged_files,
    generate_separate_files,
)
from src.app.pipeline.step_11.excel_formatter import (
    convert_to_excel_with_formatting,
)
from src.app.pipeline.step_11.runner.constants import (
    OUTPUT_MERGED_CSV,
    OUTPUT_MERGED_EXCEL,
    OUTPUT_SEPARATE_CSV,
    OUTPUT_SEPARATE_EXCEL,
)


def convert_and_count(files: list, excel_output_dir: str) -> int:
    """Convert files to Excel and return count."""
    if files:
        convert_to_excel_with_formatting(
            csv_files=files, excel_output_dir=excel_output_dir
        )
        return len(files)
    return 0


def generate_merged_output(
    combined_data, branch: str, timestamp: str
) -> int:
    """Generate merged files (all targets in one file) and convert to Excel."""
    merged_files = generate_merged_files(
        df=combined_data, branch=branch, 
        csv_output_dir=OUTPUT_MERGED_CSV, timestamp=timestamp
    )
    return convert_and_count(merged_files, OUTPUT_MERGED_EXCEL)


def generate_separate_output(
    combined_data, branch: str, timestamp: str
) -> int:
    """Generate separate files (per target branch) and convert to Excel."""
    separate_files = generate_separate_files(
        df=combined_data, branch=branch, 
        csv_output_dir=OUTPUT_SEPARATE_CSV, timestamp=timestamp
    )
    return convert_and_count(separate_files, OUTPUT_SEPARATE_EXCEL)

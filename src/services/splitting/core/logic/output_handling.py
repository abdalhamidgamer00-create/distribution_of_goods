"""Output handling logic."""

import os
from time import perf_counter
from src.services.splitting.writers.file_writer import write_branch_files, write_analytics_files

def write_output_files(branches: list, processed_data: dict, output_base_dir: str, base_filename: str,
                        analytics_dir: str, max_withdrawals: int, has_date_header: bool, 
                        first_line: str, timing_stats: dict) -> dict:
    """Write branch and analytics files."""
    write_start = perf_counter()
    output_files = write_branch_files(branches, processed_data, output_base_dir, base_filename, has_date_header, first_line)
    if analytics_dir is None:
        analytics_dir = os.path.normpath(os.path.join(output_base_dir, "..", "analytics"))
    write_analytics_files(branches, processed_data, analytics_dir, base_filename, max_withdrawals, has_date_header, first_line)
    timing_stats["write_time"] = perf_counter() - write_start
    return output_files

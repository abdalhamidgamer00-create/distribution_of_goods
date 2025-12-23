"""Filename generation logic."""

import os
import re
from datetime import datetime

def generate_output_filename(excel_file: str) -> str:
    """Generate output CSV filename with timestamp."""
    date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(excel_file)[0]
    base_name_clean = re.sub(r'_\d{8}_\d{6}', '', base_name)
    return f"{base_name_clean}_{date_string}.csv"

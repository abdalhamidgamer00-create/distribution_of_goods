"""Constants for Step 11 runner."""

import os

TRANSFERS_DIR = os.path.join("data", "output", "transfers", "csv")
REMAINING_SURPLUS_DIR = os.path.join(
    "data", "output", "remaining_surplus", "csv"
)
ANALYTICS_DIR = os.path.join("data", "output", "branches", "analytics")

OUTPUT_MERGED_CSV = os.path.join(
    "data", "output", "combined_transfers", "merged", "csv"
)
OUTPUT_MERGED_EXCEL = os.path.join(
    "data", "output", "combined_transfers", "merged", "excel"
)
OUTPUT_SEPARATE_CSV = os.path.join(
    "data", "output", "combined_transfers", "separate", "csv"
)
OUTPUT_SEPARATE_EXCEL = os.path.join(
    "data", "output", "combined_transfers", "separate", "excel"
)

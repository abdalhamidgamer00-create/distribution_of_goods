"""Centralized path configurations for the distribution system."""

import os

# Base directories
DATA_DIR = "data"
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

# Input categories
CONVERTED_DIR = os.path.join(OUTPUT_DIR, "converted")
INPUT_CSV_DIR = os.path.join(CONVERTED_DIR, "csv")
RENAMED_CSV_DIR = os.path.join(CONVERTED_DIR, "renamed")

# Output categories
ANALYTICS_DIR = os.path.join(OUTPUT_DIR, "branches", "analytics")
TRANSFERS_CSV_DIR = os.path.join(OUTPUT_DIR, "transfers", "csv")
TRANSFERS_EXCEL_DIR = os.path.join(OUTPUT_DIR, "transfers", "excel")
SURPLUS_DIR = os.path.join(OUTPUT_DIR, "remaining_surplus")
SHORTAGE_DIR = os.path.join(OUTPUT_DIR, "shortage")
COMBINED_DIR = os.path.join(OUTPUT_DIR, "combined_transfers")
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive")

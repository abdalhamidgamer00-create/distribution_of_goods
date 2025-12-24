"""Global constants and configuration values."""

from typing import Dict

# Branch Names - Enforcing Zero Abbreviations
BRANCHES = [
    "administration",
    "asherin",
    "star",
    "shahid",
    "okba",
    "wardani"
]

# Scoring Weights for Priority Calculation
PRIORITY_WEIGHTS = {
    "balance": 0.60,
    "needed": 0.30,
    "avg_sales": 0.10
}

# Inventory Constraints
STOCK_COVERAGE_DAYS = 20

# Product Types/Categories
PRODUCT_CATEGORIES = [
    "tablets_and_capsules",
    "injections",
    "syrups",
    "creams",
    "sachets",
    "other"
]

# File Path Templates
DATA_DIR = "data"
INPUT_DIR = f"{DATA_DIR}/input"
OUTPUT_DIR = f"{DATA_DIR}/output"
ARCHIVE_DIR = f"{DATA_DIR}/archive"
LOG_DIR = f"{DATA_DIR}/logs"

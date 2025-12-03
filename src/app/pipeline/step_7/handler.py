"""Step 7: Generate transfer files handler"""

import os
import re
from datetime import datetime
from src.shared.utils.file_handler import (
    get_csv_files,
    get_latest_file,
    get_file_path,
    ensure_directory_exists,
)
from src.core.domain.branches.config import get_branches
from src.services.transfers.generators.transfer_generator import generate_transfer_files
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def step_7_generate_transfers(use_latest_file: bool = None) -> bool:
    """Step 7: Generate transfer CSV files between branches"""
    analytics_dir = os.path.join("data", "output", "branches", "analytics")
    transfers_base_dir = os.path.join("data", "output", "transfers", "csv")
    
    branches = get_branches()
    
    for branch in branches:
        analytics_branch_dir = os.path.join(analytics_dir, branch)
        if not os.path.exists(analytics_branch_dir):
            logger.error("Analytics directory not found: %s", analytics_branch_dir)
            logger.error("Please run step 5 (Split by Branches) first to generate analytics files")
            return False
    
    analytics_files = {}
    for branch in branches:
        branch_files = get_csv_files(os.path.join(analytics_dir, branch))
        if branch_files:
            analytics_files[branch] = branch_files
    
    if not analytics_files:
        logger.error("No analytics files found in %s", analytics_dir)
        logger.error("Please run step 5 (Split by Branches) first to generate analytics files")
        return False
    
    try:
        has_date_header = False
        first_line = ""
        
        try:
            first_branch = list(analytics_files.keys())[0]
            latest_file = get_latest_file(os.path.join(analytics_dir, first_branch), '.csv')
            if latest_file:
                sample_analytics_path = os.path.join(analytics_dir, first_branch, latest_file)
                with open(sample_analytics_path, 'r', encoding='utf-8-sig') as f:
                    first_line = f.readline().strip()
                    from src.core.validation.data_validator import extract_dates_from_header
                    start_date, end_date = extract_dates_from_header(first_line)
                    if start_date and end_date:
                        has_date_header = True
        except Exception:
            pass
        
        logger.info("Generating transfer files...")
        logger.info("-" * 50)
        logger.info("Using latest analytics files for each target branch...")
        
        transfer_files = generate_transfer_files(analytics_dir, transfers_base_dir, has_date_header, first_line)
        
        if not transfer_files:
            logger.warning("No transfers found between branches")
            return False
        
        logger.info("Generated %s transfer files:", len(transfer_files))
        
        # تجميع الملفات حسب الفرع المصدر
        files_by_source = {}
        for (source, target), file_path in transfer_files.items():
            if source not in files_by_source:
                files_by_source[source] = []
            files_by_source[source].append((target, file_path))
        
        # عرض الملفات مجمعة مع معلومات إضافية
        for source in sorted(files_by_source.keys()):
            files_list = files_by_source[source]
            logger.info("\n  From %s (%d files):", source, len(files_list))
            for target, file_path in sorted(files_list):
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                size_str = _format_file_size(file_size)
                logger.info("    → %s: %s (%s)", target, os.path.basename(file_path), size_str)
        
        logger.info("\nTransfer files saved to: %s", transfers_base_dir)
        
        return True
        
    except ValueError as e:
        logger.error("Error: %s", e)
        return False
    except Exception as e:
        logger.exception("Error during transfer generation: %s", e)
        return False


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


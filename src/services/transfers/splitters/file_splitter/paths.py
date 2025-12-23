"""File path and name helpers."""

import os


def extract_target_branch(base_name: str) -> str:
    """Extract target branch name from file name."""
    if '_to_' in base_name:
        parts = base_name.split('_to_')
        if len(parts) > 1:
            return parts[-1]
    return None


def get_folder_name(transfer_file_path: str, base_name: str) -> str:
    """Get folder name for output, adjusting for target branch."""
    base_folder_name = os.path.basename(os.path.dirname(transfer_file_path))
    target_branch = extract_target_branch(base_name)
    
    if target_branch:
        return base_folder_name.replace(
            '_to_other_branches', f'_to_{target_branch}'
        )
    return base_folder_name


def is_already_split_file(filename: str, categories: list) -> bool:
    """Check if file is already a split category file."""
    return any(
        filename.endswith(f'_{category}.csv') for category in categories
    ) or any(filename == f'{category}.csv' for category in categories)


def find_unsplit_files(transfers_base_dir: str, categories: list) -> list:
    """Find all unsplit transfer files."""
    unsplit = []
    for root, directories, files in os.walk(transfers_base_dir):
        for filename in files:
            if filename.endswith('.csv') and not is_already_split_file(
                filename, categories
            ):
                unsplit.append(os.path.join(root, filename))
    return unsplit

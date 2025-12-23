"""Output path helpers for Excel formatter."""

import os


def get_output_subdir(
    excel_output_dir: str, folder_name: str, grandparent_name: str
) -> str:
    """Get output subdirectory based on folder structure."""
    if folder_name.startswith('to_'):
        return os.path.join(excel_output_dir, grandparent_name, folder_name)
    return os.path.join(excel_output_dir, folder_name)


def determine_output_path(csv_path: str, excel_output_dir: str) -> str:
    """Determine the output path for Excel file based on CSV structure."""
    csv_directory = os.path.dirname(csv_path)
    parent_directory = os.path.dirname(csv_directory)
    
    output_subdir = get_output_subdir(
        excel_output_dir, 
        os.path.basename(csv_directory), 
        os.path.basename(parent_directory)
    )
    os.makedirs(output_subdir, exist_ok=True)
    
    return os.path.join(
        output_subdir, 
        os.path.basename(csv_path).replace('.csv', '.xlsx')
    )

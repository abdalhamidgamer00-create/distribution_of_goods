"""Grouping helpers."""

def group_files_by_source(transfer_files: dict) -> dict:
    """Group transfer files by source branch."""
    files_by_source = {}
    for (source, target), file_path in transfer_files.items():
        if source not in files_by_source:
            files_by_source[source] = []
        files_by_source[source].append((target, file_path))
    return files_by_source

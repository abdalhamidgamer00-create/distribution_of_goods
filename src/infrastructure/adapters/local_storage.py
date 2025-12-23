"""Local file system implementation of FileStorage."""

import os
import shutil
from typing import List
from src.application.interfaces.storage import FileStorage


class LocalFileStorage(FileStorage):
    """Implementation of FileStorage using standard os/shutil modules."""

    def list_files(self, directory: str, extensions: List[str]) -> List[str]:
        """List files with matching extensions."""
        if not os.path.exists(directory):
            return []
        return [
            f for f in os.listdir(directory)
            if any(f.endswith(ext) for ext in extensions)
        ]

    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return os.path.exists(path)

    def create_directory(self, path: str) -> None:
        """Ensure directory exists."""
        os.makedirs(path, exist_ok=True)

    def delete_files(self, directory: str) -> None:
        """Clear all files in directory."""
        if not os.path.exists(directory):
            return
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception:
                # In a real system, we'd log this or raise a StorageError
                pass

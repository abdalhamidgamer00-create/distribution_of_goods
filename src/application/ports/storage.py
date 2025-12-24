"""Interface for file storage operations."""

from abc import ABC, abstractmethod
from typing import List, Optional


class FileStorage(ABC):
    """Abstract interface for file system interactions."""

    @abstractmethod
    def list_files(self, directory: str, extensions: List[str]) -> List[str]:
        """List files in a directory with specific extensions."""
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if a path exists."""
        pass

    @abstractmethod
    def create_directory(self, path: str) -> None:
        """Ensure a directory exists."""
        pass

    @abstractmethod
    def delete_files(self, directory: str) -> None:
        """Clear all files in a directory."""
        pass

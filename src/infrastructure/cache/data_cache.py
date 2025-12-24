"""In-memory cache for data snapshots to minimize redundant disk I/O."""

from typing import Any, Dict


class DataSnapshotCache:
    """Simple in-memory cache for DataFrames and domain entities."""
    
    _instance = None
    _cache: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataSnapshotCache, cls).__new__(cls)
        return cls._instance

    def set(self, key: str, value: Any) -> None:
        """Stores a value in the cache."""
        self._cache[key] = value

    def get(self, key: str) -> Any:
        """Retrieves a value from the cache or None if missing."""
        return self._cache.get(key)

    def has(self, key: str) -> bool:
        """Checks if a key exists in the cache."""
        return key in self._cache

    def clear(self) -> None:
        """Clears all cached data."""
        self._cache.clear()

    def invalidate(self, key: str) -> None:
        """Removes a specific key from the cache."""
        if key in self._cache:
            del self._cache[key]

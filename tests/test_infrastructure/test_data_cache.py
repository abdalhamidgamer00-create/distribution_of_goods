"""Unit tests for the DataSnapshotCache."""

import pytest
from src.infrastructure.cache.data_cache import DataSnapshotCache

class TestDataSnapshotCache:
    """Tests for the DataSnapshotCache singleton."""

    def setup_method(self):
        """Reset the cache instance and dictionary before each test."""
        self.cache = DataSnapshotCache()
        self.cache.clear()

    def test_singleton_instance(self):
        """Should always return the same instance."""
        cache1 = DataSnapshotCache()
        cache2 = DataSnapshotCache()
        assert cache1 is cache2

    def test_set_and_get(self):
        """Should store and retrieve values correctly."""
        self.cache.set("key", "value")
        assert self.cache.get("key") == "value"

    def test_has_key(self):
        """Should correctly identify existing keys."""
        self.cache.set("test", 123)
        assert self.cache.has("test") is True
        assert self.cache.has("missing") is False

    def test_clear_all(self):
        """Should remove all keys from cache."""
        self.cache.set("a", 1)
        self.cache.set("b", 2)
        self.cache.clear()
        assert self.cache.has("a") is False
        assert self.cache.has("b") is False

    def test_invalidate_specific_key(self):
        """Should remove only the specified key."""
        self.cache.set("keep", "safe")
        self.cache.set("delete", "me")
        self.cache.invalidate("delete")
        
        assert self.cache.has("delete") is False
        assert self.cache.get("keep") == "safe"

    def test_get_non_existent_returns_none(self):
        """Should return None for missing keys."""
        assert self.cache.get("no_exist") is None

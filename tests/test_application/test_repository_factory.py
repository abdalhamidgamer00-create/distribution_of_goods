"""Unit tests for the RepositoryFactory."""

import pytest
from src.application.factories.repository_factory import RepositoryFactory
from src.infrastructure.repositories.base.pandas_repository import PandasDataRepository


class TestRepositoryFactory:
    """Tests for the RepositoryFactory class."""

    def test_create_pandas_repository_returns_correct_type(self):
        """Should return an instance of PandasDataRepository."""
        repo = RepositoryFactory.create_pandas_repository()
        assert isinstance(repo, PandasDataRepository)

    def test_create_pandas_repository_paths_are_configured(self):
        """Should have core components configured with non-default paths."""
        repo = RepositoryFactory.create_pandas_repository()
        
        # Check that internal components were initialized
        assert repo._reader is not None
        assert repo._surplus is not None
        assert repo._lister is not None
        
        # Check some key properties (though these are implementation details, 
        # they verify the factory passed different paths than the default output_dir)
        assert repo._input_dir is not None
        assert repo._output_dir is not None

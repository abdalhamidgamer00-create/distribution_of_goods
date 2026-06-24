"""Tests for infrastructure.repositories.metadata.output_manager module."""

import os
import tempfile
import shutil

import pytest

from src.infrastructure.repositories.metadata.output_manager import (
    list_artifacts,
    _resolve_format_directory,
    _is_match,
    _extract_metadata_from_name,
    _collect_recursive,
)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _create_file(path, content="data"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)


class TestResolveFormatDirectory:
    def test_returns_subdir_when_exists(self, tmp_dir):
        csv_dir = os.path.join(tmp_dir, "csv")
        os.makedirs(csv_dir)
        result = _resolve_format_directory(tmp_dir, "csv")
        assert result == csv_dir

    def test_returns_base_when_ends_with_format(self, tmp_dir):
        csv_dir = os.path.join(tmp_dir, "csv")
        os.makedirs(csv_dir)
        result = _resolve_format_directory(csv_dir, "csv")
        assert result == csv_dir

    def test_returns_none_when_nothing_matches(self, tmp_dir):
        result = _resolve_format_directory(tmp_dir, "excel")
        assert result is None


class TestIsMatch:
    def test_pattern_in_item(self):
        assert _is_match("transfers", None, "transfers_from_admin", "transfers") is True

    def test_branch_filter_from_prefix(self):
        assert _is_match(
            "transfers", "admin", "from_admin_transfers", ""
        ) is True

    def test_branch_filter_starts_with(self):
        assert _is_match(
            "transfers", "admin", "admin_something", ""
        ) is True

    def test_no_match(self):
        assert _is_match("surplus", None, "star_data", "shortage") is False

    def test_non_transfers_category(self):
        assert _is_match("shortage", None, "something", "other") is False


class TestExtractMetadataFromName:
    def test_with_filter_val(self):
        result = _extract_metadata_from_name("transfers", "admin", "anything")
        assert result == "admin"

    def test_regex_match(self):
        result = _extract_metadata_from_name(
            "transfers", None, "transfers_from_admin_to_star"
        )
        assert "admin" in result

    def test_fallback_split(self):
        result = _extract_metadata_from_name(
            "transfers", None, "something_from_star_other"
        )
        assert result == "star"

    def test_no_from_keyword(self):
        result = _extract_metadata_from_name(
            "transfers", None, "just_a_folder"
        )
        assert result == "just_a_folder"


class TestCollectRecursive:
    def test_collects_csv_files(self, tmp_dir):
        _create_file(os.path.join(tmp_dir, "test.csv"))
        results = []
        _collect_recursive(tmp_dir, "transfers", "admin", results, tmp_dir)
        assert len(results) == 1
        assert results[0]['name'] == "test.csv"

    def test_collects_xlsx_files(self, tmp_dir):
        _create_file(os.path.join(tmp_dir, "test.xlsx"))
        results = []
        _collect_recursive(tmp_dir, "transfers", "admin", results, tmp_dir)
        assert len(results) == 1

    def test_ignores_non_csv_xlsx_files(self, tmp_dir):
        _create_file(os.path.join(tmp_dir, "test.txt"))
        results = []
        _collect_recursive(tmp_dir, "transfers", "admin", results, tmp_dir)
        assert len(results) == 0

    def test_recurses_into_subdirs(self, tmp_dir):
        _create_file(os.path.join(tmp_dir, "sub", "test.csv"))
        results = []
        _collect_recursive(tmp_dir, "transfers", "admin", results, tmp_dir)
        assert len(results) == 1

    def test_nonexistent_dir_returns_early(self):
        results = []
        _collect_recursive("/nonexistent", "transfers", "admin", results, "/nonexistent")
        assert len(results) == 0

    def test_collections_category_skips_non_collection_folders(self, tmp_dir):
        _create_file(os.path.join(tmp_dir, "test.csv"))
        results = []
        _collect_recursive(tmp_dir, "collections", "admin", results, tmp_dir)
        assert len(results) == 0

    def test_collections_category_includes_collection_folder(self, tmp_dir):
        coll_dir = os.path.join(tmp_dir, "all_transfers_collection")
        _create_file(os.path.join(coll_dir, "test.csv"))
        results = []
        _collect_recursive(coll_dir, "collections", "admin", results, tmp_dir)
        assert len(results) == 1


class TestListArtifacts:
    def test_lists_csv_files(self, tmp_dir):
        csv_dir = os.path.join(tmp_dir, "csv", "shortage_stuff")
        _create_file(os.path.join(csv_dir, "report.csv"))
        results = list_artifacts(
            "shortage", tmp_dir, {'csv': 'shortage', 'excel': 'shortage'}
        )
        assert len(results) >= 1

    def test_empty_directory_returns_empty(self, tmp_dir):
        os.makedirs(os.path.join(tmp_dir, "csv"), exist_ok=True)
        results = list_artifacts(
            "transfers", tmp_dir, {'csv': 'transfers', 'excel': 'transfers'}
        )
        assert results == []

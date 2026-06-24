"""Tests for infrastructure.repositories.metadata.artifact_metadata module."""

import os
import tempfile
import shutil

import pytest

from src.infrastructure.repositories.metadata.artifact_metadata import (
    create_artifact_metadata,
    enrich_separate_metadata,
    _extract_branch_category,
)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestCreateArtifactMetadata:
    def test_basic_metadata_fields(self, tmp_dir):
        filepath = os.path.join(tmp_dir, "test.csv")
        with open(filepath, 'w') as f:
            f.write("data")

        meta = create_artifact_metadata(
            "test.csv", filepath, "transfers", "admin", "folder1"
        )
        assert meta['name'] == "test.csv"
        assert meta['category'] == "transfers"
        assert meta['branch'] == "admin"
        assert meta['folder_name'] == "folder1"
        assert meta['size'] == 4
        assert 'mtime' in meta

    def test_relative_path_with_root_dir(self, tmp_dir):
        subdir = os.path.join(tmp_dir, "sub")
        os.makedirs(subdir)
        filepath = os.path.join(subdir, "test.csv")
        with open(filepath, 'w') as f:
            f.write("data")

        meta = create_artifact_metadata(
            "test.csv", filepath, "transfers", "admin", "sub",
            root_dir=tmp_dir
        )
        assert meta['relative_path'] == os.path.join("sub", "test.csv")

    def test_relative_path_without_root_dir(self, tmp_dir):
        filepath = os.path.join(tmp_dir, "test.csv")
        with open(filepath, 'w') as f:
            f.write("data")

        meta = create_artifact_metadata(
            "test.csv", filepath, "surplus", "star", "folder"
        )
        assert meta['relative_path'] == "test.csv"

    def test_path_is_absolute(self, tmp_dir):
        filepath = os.path.join(tmp_dir, "test.csv")
        with open(filepath, 'w') as f:
            f.write("data")

        meta = create_artifact_metadata(
            "test.csv", filepath, "shortage", "okba", "folder"
        )
        assert os.path.isabs(meta['path'])


class TestEnrichSeparateMetadata:
    def test_sets_source_and_target_folders(self, tmp_dir):
        search_dir = os.path.join(tmp_dir, "source_folder", "target_folder")
        os.makedirs(search_dir)

        meta = {}
        enrich_separate_metadata(
            meta, search_dir, "admin_to_star_tablets.csv", "target_folder"
        )
        assert meta['source_folder'] == "source_folder"
        assert meta['target_folder'] == "target_folder"

    def test_extracts_branch_and_category(self, tmp_dir):
        search_dir = os.path.join(tmp_dir, "src", "tgt")
        os.makedirs(search_dir)

        meta = {}
        enrich_separate_metadata(
            meta, search_dir, "admin_to_star_tablets.csv", "tgt"
        )
        assert meta.get('target_branch') == "star"
        assert meta.get('product_category') == "tablets"

    def test_no_to_in_filename(self, tmp_dir):
        search_dir = os.path.join(tmp_dir, "src", "tgt")
        os.makedirs(search_dir)

        meta = {}
        enrich_separate_metadata(
            meta, search_dir, "no_branch_info.csv", "tgt"
        )
        assert 'target_branch' not in meta
        assert 'product_category' not in meta


class TestExtractBranchCategory:
    def test_valid_stem(self):
        meta = {}
        _extract_branch_category(meta, "admin_to_star_tablets")
        assert meta['target_branch'] == "star"
        assert meta['product_category'] == "tablets"

    def test_no_to_keyword(self):
        meta = {}
        _extract_branch_category(meta, "admin_star_tablets")
        assert 'target_branch' not in meta

    def test_index_error_on_short_stem(self):
        meta = {}
        _extract_branch_category(meta, "from_to")
        assert 'product_category' not in meta

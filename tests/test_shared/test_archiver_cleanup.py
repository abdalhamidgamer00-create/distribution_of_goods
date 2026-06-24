"""Tests for shared.utility.archiver.cleanup module."""

import os
import tempfile
import shutil

import pytest

from src.shared.utility.archiver.cleanup import (
    delete_directory_contents,
    handle_empty_directory,
    delete_and_verify,
    try_clear_directory,
    clear_output_directory,
)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestDeleteDirectoryContents:
    def test_deletes_files(self, tmp_dir):
        with open(os.path.join(tmp_dir, "file.txt"), 'w') as f:
            f.write("data")
        delete_directory_contents(tmp_dir)
        assert os.listdir(tmp_dir) == []

    def test_deletes_subdirectories(self, tmp_dir):
        subdir = os.path.join(tmp_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "file.txt"), 'w') as f:
            f.write("data")
        delete_directory_contents(tmp_dir)
        assert os.listdir(tmp_dir) == []

    def test_empty_directory_no_error(self, tmp_dir):
        delete_directory_contents(tmp_dir)
        assert os.listdir(tmp_dir) == []


class TestHandleEmptyDirectory:
    def test_empty_returns_true(self):
        result = handle_empty_directory(0, 0)
        assert result is True

    def test_non_empty_returns_none(self):
        result = handle_empty_directory(5, 2)
        assert result is None

    def test_files_only_returns_none(self):
        result = handle_empty_directory(5, 0)
        assert result is None


class TestDeleteAndVerify:
    def test_successful_deletion(self, tmp_dir):
        with open(os.path.join(tmp_dir, "file.txt"), 'w') as f:
            f.write("data")
        result = delete_and_verify(tmp_dir, 1, 0)
        assert result is True

    def test_with_subdirs(self, tmp_dir):
        subdir = os.path.join(tmp_dir, "sub")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "file.txt"), 'w') as f:
            f.write("data")
        result = delete_and_verify(tmp_dir, 1, 1)
        assert result is True


class TestTryClearDirectory:
    def test_clears_non_empty_directory(self, tmp_dir):
        with open(os.path.join(tmp_dir, "file.txt"), 'w') as f:
            f.write("data")
        result = try_clear_directory(tmp_dir)
        assert result is True
        assert os.listdir(tmp_dir) == []

    def test_handles_empty_directory(self, tmp_dir):
        result = try_clear_directory(tmp_dir)
        assert result is True


class TestClearOutputDirectory:
    def test_nonexistent_directory_returns_true(self):
        result = clear_output_directory("/nonexistent/path/to/dir")
        assert result is True

    def test_clears_existing_directory(self, tmp_dir):
        with open(os.path.join(tmp_dir, "file.txt"), 'w') as f:
            f.write("data")
        result = clear_output_directory(tmp_dir)
        assert result is True
        assert os.listdir(tmp_dir) == []
